
import os
import asyncio
import logging
import html
import feedparser

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEWS_FEED = "https://feeds.bbci.co.uk/sport/football/rss.xml"

MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📰 Latest News", callback_data="news"),
        InlineKeyboardButton("📅 Fixtures", callback_data="fixtures"),
    ],
    [
        InlineKeyboardButton("🏆 Results", callback_data="results"),
        InlineKeyboardButton("⚽ Team Updates", callback_data="teams"),
    ],
    [
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("❓ Help", callback_data="help"),
    ],
])

def get_latest_news():
    feed = feedparser.parse(NEWS_FEED)
    articles = feed.entries[:5]
    if not articles:
        return None

    lines = ["📰 <b>Latest Football News</b>\n"]
    for article in articles:
        title = html.escape(article.get("title", "Football update"))
        link = article.get("link", "")
        if link.startswith("https://"):
            lines.append(f'• <a href="{html.escape(link, quote=True)}">{title}</a>')
        else:
            lines.append(f"• {title}")

    return "\n\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "⚽ <b>Welcome to Football News &amp; Updates!</b>\n\n"
        "Get football headlines, upcoming fixture information, "
        "match results, and team updates.\n\n"
        "Choose an option below to get started:"
    )
    await update.effective_message.reply_text(
        message,
        reply_markup=MENU,
        parse_mode="HTML",
    )

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    if query.data == "news":
        await query.edit_message_text("⏳ Loading the latest football headlines...")
        try:
            news = await asyncio.to_thread(get_latest_news)
            if news:
                await query.edit_message_text(
                    news,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Main Menu", callback_data="menu")]
                    ]),
                    disable_web_page_preview=True,
                )
            else:
                await query.edit_message_text(
                    "Sorry, football news is temporarily unavailable. "
                    "Please try again later.",
                    reply_markup=MENU,
                )
        except Exception:
            logger.exception("Could not load football news")
            await query.edit_message_text(
                "News is temporarily unavailable. Please try again later.",
                reply_markup=MENU,
            )

    elif query.data == "fixtures":
        await query.edit_message_text(
            "📅 <b>Upcoming Football Fixtures</b>\n\n"
            "View upcoming match schedules here:\n"
            "https://www.bbc.com/sport/football/scores-fixtures",
            parse_mode="HTML",
            reply_markup=MENU,
            disable_web_page_preview=True,
        )

    elif query.data == "results":
        await query.edit_message_text(
            "🏆 <b>Football Results</b>\n\n"
            "Check recent scores and completed matches here:\n"
            "https://www.bbc.com/sport/football/scores-fixtures",
            parse_mode="HTML",
            reply_markup=MENU,
            disable_web_page_preview=True,
        )

    elif query.data == "teams":
        await query.edit_message_text(
            "⚽ <b>Club and Team Updates</b>\n\n"
            "Read the latest football team news here:\n"
            "https://www.bbc.com/sport/football",
            parse_mode="HTML",
            reply_markup=MENU,
            disable_web_page_preview=True,
        )

    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ <b>About This Bot</b>\n\n"
            "Football News & Updates shares football headlines "
            "and links to match schedules, results, and team news.\n\n"
            "This bot is an independent football information service.",
            parse_mode="HTML",
            reply_markup=MENU,
        )

    elif query.data == "help":
        await query.edit_message_text(
            "❓ <b>How to Use This Bot</b>\n\n"
            "• Tap Latest News to read recent headlines.\n"
            "• Tap Fixtures to view match schedules.\n"
            "• Tap Results to check scores.\n"
            "• Tap Team Updates to read football news.\n\n"
            "Use /start anytime to reopen the menu.",
            parse_mode="HTML",
            reply_markup=MENU,
        )

    elif query.data == "menu":
        await query.edit_message_text(
            "⚽ <b>Football News &amp; Updates</b>\n\n"
            "Choose an option below:",
            parse_mode="HTML",
            reply_markup=MENU,
        )

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await start(update, context)

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Please set the BOT_TOKEN environment variable.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Football News Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
