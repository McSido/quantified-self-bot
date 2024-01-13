import json
import logging
from dotenv import load_dotenv
import os

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Updater,
    filters,
)

# Load questions from JSON file
with open("questions.json", "r") as file:
    questions = json.load(file)

# Define states for ConversationHandler
QUESTION, RESPONSE = range(2)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! I will start asking you questions.")
    return await ask_question(update, context)


async def ask_question(update: Update, context: CallbackContext) -> int:
    """Function to ask the next question with inline keyboard options."""
    question = questions.pop(0)  # Get the next question
    context.user_data["current_question"] = question  # Store current question

    print(f"Next question: {question['question']}")
    # print(update, context)

    options = [
        InlineKeyboardButton(option, callback_data=option)
        for option in question["options"]
    ]

    # Make options nested by splitting into chunks of 3
    options = [options[i : i + 3] for i in range(0, len(options), 3)]

    print(options)

    # Create inline keyboard options
    keyboard = options

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(question["question"], reply_markup=reply_markup)
    return RESPONSE


async def handle_response(update: Update, context: CallbackContext) -> int:
    """Handle the user response from inline keyboard."""
    query = update.callback_query
    await query.answer()

    user_response = query.data
    current_question = context.user_data["current_question"]

    print(f"User {query.from_user.id} answered {user_response} for {current_question}")

    # Store in DB (implement actual DB logic)
    user_id = query.from_user.id
    store_in_db(user_id, current_question["question"], user_response)

    if questions:
        return await ask_question(query, context)
    else:
        await query.message.reply_text("Thank you for answering all questions!")
        return ConversationHandler.END


def store_in_db(user_id, question, response):
    """Store the response in the SQLite database."""
    # TODO: Implement database storage logic here
    pass


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the conversation."""
    await update.message.reply_text("Bye!")
    return ConversationHandler.END


def main():
    # Token from BotFather
    # Load from .env file
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Initialize bot and updater
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT, ask_question)],
            RESPONSE: [CallbackQueryHandler(handle_response)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
