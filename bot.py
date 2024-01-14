import logging
from collections.abc import Callable
from datetime import datetime

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

# Define states for ConversationHandler
QUESTION, RESPONSE = range(2)


class QuestionsBot:
    """Telegram bot class.
    Responsible for handling all Telegram bot related functionality.
    """

    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(__name__)

    def __init__(self, token: str, questions: list, persist_response: Callable):
        """Initialize the bot."""
        application = Application.builder().token(token).build()

        # Add command handlers
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                QUESTION: [MessageHandler(filters.TEXT, self.ask_question)],
                RESPONSE: [CallbackQueryHandler(self.handle_response)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        application.add_handler(conv_handler)
        self._questions = questions
        self._persist_response = persist_response
        self._application = application

    def run(self):
        """Start the bot."""
        self._application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start(self, update: Update, context: CallbackContext) -> int:
        """Send a message when the command /start is issued."""
        await update.message.reply_text("Hi! I will start asking you questions.")
        return await self.ask_question(update, context)

    async def ask_question(self, update: Update, context: CallbackContext) -> int:
        """Function to ask the next question with inline keyboard options."""
        question = self._questions.pop(0)
        context.user_data["current_question"] = question

        options = [
            InlineKeyboardButton(option, callback_data=option)
            for option in question["options"]
        ]

        # Add next button if question is multiple choice

        if "multiple" in question and question["multiple"]:
            options.append(InlineKeyboardButton("Next", callback_data="<next>"))

        # Make options nested by splitting into chunks of 3
        options = [options[i : i + 3] for i in range(0, len(options), 3)]
        # Create inline keyboard options
        keyboard = options

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(question["question"], reply_markup=reply_markup)
        return RESPONSE

    async def handle_response(self, update: Update, context: CallbackContext) -> int:
        """Handle the user response from inline keyboard."""
        query = update.callback_query
        await query.answer()

        user_response = query.data
        current_question = context.user_data["current_question"]
        user_id = query.from_user.id

        is_multiple = "multiple" in current_question and current_question["multiple"]

        if is_multiple:
            if user_response != "<next>":
                self._persist_response(
                    user_id, current_question["question"], user_response
                )
                return RESPONSE
        else:
            self._persist_response(user_id, current_question["question"], user_response)

        # Check if there are more questions
        if self._questions:
            return await self.ask_question(query, context)
        else:
            await query.message.reply_text("Thank you for answering all questions!")
            return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancel the conversation."""
        await update.message.reply_text("Bye!")
        return ConversationHandler.END
