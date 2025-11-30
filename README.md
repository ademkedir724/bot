# Anonymous Comment Telegram Bot

This project provides a complete, production-ready Telegram bot that allows users to send anonymous comments about a predefined set of people to a specific group.

It's built with Python, `python-telegram-bot`, `asyncpg`, and is fully containerized with Docker and Docker Compose for easy setup and deployment.

## Features

- **Anonymous Forwarding**: Forwards comments to a group without revealing the sender's identity.
- **Conversation Flow**: Guides users through selecting a person and submitting a comment.
- **Rate Limiting**: Prevents users from spamming comments.
- **Profanity Filter**: A basic filter to block messages with disallowed words.
- **Database Persistence**: Stores comments and user data in a PostgreSQL database, so data is safe across restarts.
- **Dockerized**: Easy to set up and run with a single command.

---

## How to Run

### Prerequisites

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Usually included with Docker Desktop. If not, [install Docker Compose](https://docs.docker.com/compose/install/).
- **Telegram Bot Token**: Get one from the [BotFather](https://t.me/botfather).
- **Telegram Group**: A group where the bot and the three target individuals are members.

### Step 1: Create a `.env` File

At the root of the project, create a file named `.env`. This file will hold your secret credentials.

```
# .env

# Your Telegram Bot Token from BotFather
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123456789

# The ID of the group where comments will be sent
GROUP_CHAT_ID=-1001234567890

# (Optional) Cooldown time in seconds between comments for a single user
# RATE_LIMIT_SECONDS=120

# (Optional) Comma-separated list of words to block
# PROFANITY_WORDS=word1,word2,another
```

### Step 2: Find Your `GROUP_CHAT_ID`

To get the `GROUP_CHAT_ID`, follow these steps **safely**:

1.  Add your new bot to your target Telegram group.
2.  Send any message to the group (e.g., "hello").
3.  Open your web browser and go to the following URL, replacing `<YOUR_BOT_TOKEN>` with your actual token:
    ```
    https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
    ```
4.  Look for the JSON response. You will see something like this:
    ```json
    {
      "ok": true,
      "result": [
        {
          "update_id": 8393,
          "message": {
            "chat": {
              "id": -1001234567890,  // <-- This is your GROUP_CHAT_ID
              "title": "My Test Group",
              "type": "supergroup"
            },
            ...
          }
        }
      ]
    }
    ```
5.  Copy the `id` value from the `chat` object. It's a negative number. This is your `GROUP_CHAT_ID`.
6.  Paste this value into your `.env` file.

**Security Note**: After you get the ID, it's a good practice to clear the chat history in the group or send a few more messages to push the `getUpdates` history.

### Step 3: Launch the Bot

With your `.env` file ready, open your terminal in the project's root directory and run:

```bash
docker compose up --build
```

This command will:
1.  Build the Docker image for the bot.
2.  Start the PostgreSQL database container.
3.  Wait for the database to be ready.
4.  Run the database schema migrations.
5.  Start the bot.

Your bot is now running! You can interact with it on Telegram. To stop it, press `Ctrl+C` in your terminal. To run it in the background, use `docker compose up --build -d`.

---

## Customization

### Changing the Targets

To change the three people the user can select, edit the `TARGETS` dictionary in `app/settings.py`:

```python
# app/settings.py
...
#           KEY      NAME DISPLAYED TO USER
TARGETS = {"A": "Person A", "B": "Person B", "C": "Person C"}
```

You can change the names or add more options. The `key` ("A", "B", "C") is what's stored in the database.

### Adjusting Rate Limit & Profanity

You can control the rate limit and profanity words directly in your `.env` file using the `RATE_LIMIT_SECONDS` and `PROFANITY_WORDS` variables. If they are not set in the `.env` file, the bot will use the default values from `app/settings.py`.

---

## Project Structure

```
telegram-anon-bot/
├─ app/
│  ├─ main.py          # Main bot application logic (ConversationHandler)
│  ├─ db.py            # Async database functions (PostgreSQL)
│  ├─ settings.py      # Configuration loader (from environment)
│  └─ filters.py       # Profanity and rate-limit check functions
├─ migrations/
│  └─ init.sql         # SQL script to create database tables
├─ .env                # (You create this) Holds secrets
├─ Dockerfile          # Instructions to build the bot's Docker image
├─ docker-compose.yml  # Orchestrates the bot and database services
├─ requirements.txt    # Python package dependencies
└─ README.md           # This file
```
