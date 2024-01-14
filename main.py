import json
import os

from dotenv import load_dotenv

from bot import QuestionsBot
from persistence import ResponseDatabase


def main():
    # Load questions from JSON file
    with open("questions.json", "r") as file:
        questions = json.load(file)

    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    DB_NAME = os.getenv("DB_NAME")
    TABLE_NAME = os.getenv("TABLE_NAME")

    # Initialize database

    with ResponseDatabase(DB_NAME, TABLE_NAME) as connection:
        # Initialize bot
        bot = QuestionsBot(TELEGRAM_TOKEN, questions, connection.store)
        print("Starting bot...")
        bot.run()


if __name__ == "__main__":
    main()
