import requests
from newspaper import Article
import logging
from typing import List, Dict

# ---- CONFIGURATION ----
NEWS_API_KEY = "61bd54ad00314ae2b158e7137ebeaf7e"  # Replace with your actual key
BASE_URL = "https://newsapi.org/v2/everything"
HEADERS = {"User-Agent": "NewsLLMScraper/1.0"}

# ---- LOGGING ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ---- HELPER FUNCTION TO GET FULL TEXT ----
def extract_article_content(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        logging.warning(f"Failed to extract content from {url}: {e}")
        return ""

# ---- MAIN SCRAPER FUNCTION ----
def fetch_news_articles(keyword: str, max_results: int = 10) -> List[Dict]:
    params = {
        "q": keyword,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_results,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = data.get("articles", [])
        cleaned_articles = []

        for article in articles:
            url = article.get("url")
            full_text = extract_article_content(url)

            cleaned = {
                "title": article.get("title"),
                "description": article.get("description"),
                "url": url,
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
                "content": full_text
            }
            cleaned_articles.append(cleaned)

        logging.info(f"Fetched {len(cleaned_articles)} articles for keyword '{keyword}'")
        return cleaned_articles

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []

# ---- SAMPLE USAGE ----
if __name__ == "__main__":
    user_input = input("Enter keyword to search news: ").strip()
    news_data = fetch_news_articles(user_input)

    for i, article in enumerate(news_data, 1):
        print(f"{i}. {article['title']} ({article['source']})")
        print(f"   Published: {article['published_at']}")
        print(f"   Link: {article['url']}")
        print(f"   Content Preview: {article['content'][:200]}...\n")
