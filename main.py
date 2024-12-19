import asyncio
import feedparser
import html
from telegram.ext import Application
from telegram import Bot

# Replace with your actual values
TELEGRAM_BOT_TOKEN = '7702872525:AAGOqiiHYODfObE9YLaWY2sDvPxXRzvmWCc'
CHAT_USERNAME = '@yangiliklar25_7'  # Use the @username of your channel/group

RSS_FEEDS = [
    'https://kun.uz/news/rss',
    'https://www.gazeta.uz/oz/rss/',
    'https://www.spot.uz/oz/rss/',
    'https://uz24.uz/uz/articles.rss',
]

# Initialize the application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot = application.bot

# Store the last published links for each feed to avoid sending duplicates
latest_entries = {}


async def fetch_and_send_news():
    """Fetch the latest RSS feed entries and send them to Telegram."""
    global latest_entries

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            for entry in feed.entries:
                # Skip if the entry was already sent
                if feed_url in latest_entries and entry.link in latest_entries[
                        feed_url]:
                    continue

                # Update the latest entry for this feed
                if feed_url not in latest_entries:
                    latest_entries[feed_url] = []
                latest_entries[feed_url].append(entry.link)

                # Decode HTML entities in title and summary
                title = html.unescape(entry.title)
                summary = html.unescape(entry.summary)
                link = entry.link
                channellink = f'https://t.me/yangiliklar25_7'

                # Truncate summary if too long
                summary = summary[:300] + '...' if len(
                    summary) > 300 else summary

                follow_caption = "\n\n📢 *Join our channel for more updates!*"
                message = (
                    f"*⚡️⚡️⚡️ {title}*\n\n"
                    f"{summary}\n\n"
                    f"Maqolani to'liq o'qish: [Manbaa]({link})\n\n"
                    f"*Bizning kanalimiz* [A'zo bo'lish]({channellink})")

                image_url = None
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'media_thumbnail' in entry:
                    image_url = entry.media_thumbnail[0]['url']

                try:
                    if image_url:
                        await bot.send_photo(chat_id=CHAT_USERNAME,
                                             photo=image_url,
                                             caption=message,
                                             parse_mode="Markdown")
                    else:
                        await bot.send_message(chat_id=CHAT_USERNAME,
                                               text=message,
                                               parse_mode="Markdown")
                    print(f"Sent: {title}")
                except Exception as e:
                    # Handle flood control and other exceptions
                    if "Too Many Requests" in str(e):
                        retry_after = int(
                            str(e).split("retry after ")[-1].split(" ")[0])
                        print(
                            f"Flood control triggered. Retrying after {retry_after} seconds..."
                        )
                        await asyncio.sleep(retry_after + 1)
                        continue
                    else:
                        print(f"Error sending message: {e}")

                # Respect rate limits (e.g., wait 3 seconds between messages)
                await asyncio.sleep(3)


async def main_loop():
    """Main loop to fetch and send news periodically."""
    while True:
        await fetch_and_send_news()
        await asyncio.sleep(300)  # Wait 5 minutes before checking again


async def start_polling_and_loop():
    """Start both polling and the main loop concurrently."""
    await application.initialize()  # Initialize the bot
    asyncio.create_task(
        application.start())  # Run polling without stopping the loop
    await main_loop()  # Keep fetching news


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(start_polling_and_loop())
        loop.run_forever()  # Keeps the loop running indefinitely
    except Exception as e:
        print(f"Error: {e}")
