import feedparser
from newspaper import Article
import logging
from typing import List, Dict

# ---- CONFIG ----
RSS_FEEDS = [
    "https://www.indiatoday.in/rss/home",  # India Today
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",  # TOI
    "https://rss.ndtv.com/rss/ndtvnews-topstories.xml",  # NDTV
    "https://www.thehindu.com/news/national/feeder/default.rss"  # The Hindu
]

# ---- LOGGING SETUP ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ---- FUNCTION TO EXTRACT FULL CONTENT ----
def extract_article_text(url: str) -> str:
    """Use newspaper3k to extract full article content."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.warning(f"Failed to extract content from {url}: {e}")
        return ""

# ---- FUNCTION TO PARSE RSS ----
def fetch_news_from_rss(keyword: str, max_results: int = 10) -> List[Dict]:
    keyword = keyword.lower()
    matched_articles = []

    for feed_url in RSS_FEEDS:
        logging.info(f"Parsing feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")

            content_to_check = (title + summary).lower()
            if keyword in content_to_check:
                full_text = extract_article_text(link)
                matched_articles.append({
                    "title": title,
                    "summary": summary,
                    "url": link,
                    "published": published,
                    "content": full_text
                })

            if len(matched_articles) >= max_results:
                break

        if len(matched_articles) >= max_results:
            break

    logging.info(f"Found {len(matched_articles)} matching articles for keyword '{keyword}'")
    return matched_articles

# ---- SAMPLE USAGE ----
if __name__ == "__main__":
    user_input = input("Enter keyword to search in RSS feeds: ").strip()
    news_items = fetch_news_from_rss(user_input)

    for i, article in enumerate(news_items, 1):
        print(f"{i}. {article['title']}")
        print(f"   Published: {article['published']}")
        print(f"   Link: {article['url']}")
        print(f"   Summary: {article['summary'][:150]}...")
        print()
