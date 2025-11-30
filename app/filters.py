# app/filters.py
from datetime import datetime, timezone, timedelta
from app.settings import RATE_LIMIT_SECONDS, PROFANITY_WORDS

def contains_profanity(text: str) -> bool:
    """
    Checks if the given text contains any profanity.
    Case-insensitive check.
    """
    lower_text = text.lower()
    for word in PROFANITY_WORDS:
        # Strip whitespace from config word and check if it's not empty
        clean_word = word.strip()
        if clean_word and clean_word in lower_text:
            return True
    return False

def allowed_by_rate_limit(last_comment_at: datetime | None) -> tuple[bool, int]:
    """
    Checks if a user is allowed to comment based on the rate limit.

    Args:
        last_comment_at: A timezone-aware datetime object of the last comment, or None.

    Returns:
        A tuple of (allowed, retry_after_seconds).
        `retry_after_seconds` is 0 if allowed.
    """
    # If user has never commented, they are allowed.
    if last_comment_at is None:
        return True, 0

    # Ensure last_comment_at is timezone-aware for correct comparison
    if last_comment_at.tzinfo is None:
        last_comment_at = last_comment_at.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    time_since_last_comment = (now - last_comment_at).total_seconds()

    if time_since_last_comment >= RATE_LIMIT_SECONDS:
        return True, 0
    else:
        retry_after = int(RATE_LIMIT_SECONDS - time_since_last_comment)
        return False, retry_after
