# Quantified self Telegram bot

This is a Telegram bot that allows you to track your daily activities and get statistics about them.

## How to use

1. Create a Telegram bot using [BotFather](https://t.me/botfather)
2. Rename `sample_questions.json` to `questions.json` and fill it with your questions
3. Add token to `.env` file (see `.env.sample`)
4. Add SQLite database path to `.env` file (see `.env.sample`)
5. Add table name to `.env` file (see `.env.sample`)
6. Install dependencies using `pip3 install -r requirements.txt`
7. Start the bot using `python3 bot.py`

## Database structure

The database contains one table with the following columns:

* `id` - unique identifier of the record
* `user_id` - Telegram user ID
* `created_at` - date and time of the record creation
* `question` - question text
* `answer` - answer text
