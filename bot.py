import os
import logging
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables (local dev). On Railway, variables come from the dashboard.
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Simple in-memory quiz bank ----------
QUIZ_BANK = [
    {"q": "What is 7 × 8?", "a": "56"},
    {"q": "What is the capital of France?", "a": "paris"},
    {"q": "What is the chemical symbol for water?", "a": "h2o"},
    {"q": "How many continents are there?", "a": "7"},
    {"q": "What is 15% of 200?", "a": "30"},
    {"q": "Who wrote 'Romeo and Juliet'?", "a": "shakespeare"},
]

# Store current question per user
user_quiz_state = {}


# ---------- Command Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to EduAssistBot!\n\n"
        "I'm your study companion. Here's what I can do:\n\n"
        "/quiz - Get a random quiz question\n"
        "/answer <your answer> - Submit your answer\n"
        "/define <word> - Get a word definition (coming soon)\n"
        "/calc <expression> - Quick math calculation\n"
        "/help - Show this help message\n\n"
        "Send me any text and I'll echo it back while I learn more!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *EduAssistBot Commands*\n\n"
        "/start - Welcome message\n"
        "/quiz - Start a quiz question\n"
        "/answer <text> - Answer the current quiz\n"
        "/calc <expression> - Calculate math (e.g. /calc 2+2*3)\n"
        "/help - Show this message",
        parse_mode="Markdown",
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question = random.choice(QUIZ_BANK)
    user_quiz_state[user_id] = question["a"].lower()
    await update.message.reply_text(f"🧠 Quiz Time!\n\n{question['q']}")


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_quiz_state:
        await update.message.reply_text("No active quiz. Type /quiz to start one!")
        return

    user_answer = " ".join(context.args).strip().lower()
    correct = user_quiz_state[user_id]

    if user_answer == correct:
        await update.message.reply_text("✅ Correct! Well done.")
        del user_quiz_state[user_id]
    else:
        await update.message.reply_text(
            f"❌ Not quite. Try again or type /quiz for a new question."
        )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /calc 2+2*3")
        return

    expression = " ".join(context.args)
    # Safe-ish evaluation: only allow digits, operators, parentheses, dot, spaces
    allowed = set("0123456789+-*/().% ")
    if not set(expression).issubset(allowed):
        await update.message.reply_text("⚠️ Only numbers and + - * / ( ) . % are allowed.")
        return

    try:
        result = eval(expression, {"__builtins__": None}, {})
        await update.message.reply_text(f"🧮 {expression} = {result}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not calculate: {e}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"You said: {update.message.text}\n\n(Type /help to see what I can do.)"
    )


# ---------- Main ----------
def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN is not set. Add it to your environment.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("answer", answer))
    app.add_handler(CommandHandler("calc", calc))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("EduAssistBot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
