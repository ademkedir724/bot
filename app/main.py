# app/main.py
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from app.settings import BOT_TOKEN, GROUP_CHAT_ID, TARGETS
from app.db import init_db, close_db, save_comment, get_user_last_comment
from app.filters import contains_profanity, allowed_by_rate_limit

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SELECT_TARGET, WAIT_COMMENT = range(2)

# In-memory state to hold the chosen target for a user.
# Note: This is a simple approach. For a bot that needs to scale or be
# persistent across restarts, consider using context.user_data or a database/Redis.
user_target = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to select a target."""
    keyboard = [
        [InlineKeyboardButton(name, callback_data=key)]
        for key, name in TARGETS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Hello! Please select who you'd like to comment on:", reply_markup=reply_markup
    )
    return SELECT_TARGET


async def select_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the target selection and asks for the comment."""
    query = update.callback_query
    await query.answer()

    target_key = query.data
    user_id = query.from_user.id

    # Check if user is blocked or rate-limited before allowing them to write
    user_record = await get_user_last_comment(user_id)
    if user_record and user_record["blocked"]:
        await query.edit_message_text(
            text="You are currently blocked from submitting comments."
        )
        return ConversationHandler.END

    # Store the chosen target temporarily
    user_target[user_id] = target_key
    target_name = TARGETS[target_key]

    await query.edit_message_text(
        f"You have selected {target_name}.\n\nPlease write your anonymous comment and send it."
    )
    return WAIT_COMMENT


async def receive_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives, validates, and forwards the comment."""
    user_id = update.message.from_user.id
    comment_text = update.message.text

    # Retrieve the stored target for this user
    target_key = user_target.get(user_id)
    if not target_key:
        await update.message.reply_text(
            "Your session has expired. Please use /start to begin again."
        )
        return ConversationHandler.END

    # --- Validation ---
    # 1. Profanity check
    if contains_profanity(comment_text):
        await update.message.reply_text(
            "Your message appears to contain inappropriate language. Please revise it and send again."
        )
        # Stay in the same state to allow user to re-submit
        return WAIT_COMMENT

    # 2. Rate limit check
    user_record = await get_user_last_comment(user_id)
    last_time = user_record["last_comment_at"] if user_record else None
    is_allowed, retry_after = allowed_by_rate_limit(last_time)

    if not is_allowed:
        await update.message.reply_text(
            f"You are sending comments too quickly. Please wait {retry_after} more seconds."
        )
        # Stay in the same state
        return WAIT_COMMENT

    # --- Processing ---
    try:
        # Save the comment to the database
        await save_comment(target_key, comment_text, user_id)

        # Format and send the message to the group ANONYMOUSLY
        target_name = TARGETS[target_key]
        message_to_group = (
            f"📌 *New Anonymous Comment*\n\n"
            f"🎯 **Target:** {target_name}\n\n"
            f"💬 **Comment:**\n{comment_text}"
        )

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID, text=message_to_group, parse_mode="Markdown"
        )

        await update.message.reply_text(
            "Thank you! Your anonymous comment has been delivered."
        )

    except Exception as e:
        logger.error(f"Error processing comment for user {user_id}: {e}", exc_info=True)
        await update.message.reply_text(
            "Sorry, there was an error delivering your comment. Please try again later."
        )

    # Clean up the temporary state and end the conversation
    user_target.pop(user_id, None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user_id = update.effective_user.id
    user_target.pop(user_id, None)  # Clean up state
    await update.message.reply_text(
        "Action cancelled. Use /start to begin again."
    )
    return ConversationHandler.END


async def on_startup(application):
    """Function to run on application startup."""
    await init_db()
    logger.info("Database connection pool initialized.")


async def on_shutdown(application):
    """Function to run on application shutdown."""
    await close_db()
    logger.info("Database connection pool closed.")


def main() -> None:
    """Run the bot."""
    # Build the application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_TARGET: [
                CallbackQueryHandler(select_target)
            ],
            WAIT_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_comment)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    # Add lifecycle hooks
    application.post_init.append(on_startup)
    application.post_shutdown.append(on_shutdown)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
