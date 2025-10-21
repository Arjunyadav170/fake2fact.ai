#all in one
import feedparser
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import json
all_news = []
# for all website that provide RSS feeds

rss_feeds = {
    "PolitiFact": "https://www.politifact.com/rss/factchecks/",
    "FactCheck.org": "https://www.factcheck.org/feed/",
    "Snopes": "https://www.snopes.com/feed/",
    "AltNews": "https://www.altnews.in/feed/"
}

for source_name, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        article = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "published": datetime(*entry.published_parsed[:6]).isoformat() if "published_parsed" in entry else None,
            "summary": entry.get("summary", ""),
            "source": source_name
        }
        all_news.append(article)



# for all website that provide API (like google fact checker API)


API_KEY = "AIzaSyDK34fI2_pvVCg_5PtomSvuvPpKHerPI4I"
queries = [
    "health", "medicine", "disease", "pandemic", "vaccine", "cure",
    "climate", "environment", "weather", "science", "technology",
    "politics", "election", "government", "policy", "law", "justice",
    "education", "history", "religion", "culture", "myths", "conspiracy",
    "economy", "finance", "business", "inflation", "jobs", "trade",
    "war", "conflict", "international", "diplomacy", "migration",
    "AI", "cybersecurity", "internet", "privacy", "social media", "data",
    "hoax", "fake news", "misinformation", "rumor", "fact check"
]



for query in queries:
   params = {
        "query": query,
        "languageCode": "en",
        "maxAgeDays": 200,
        "pageSize": 10
    }
   try:
    r = requests.get(
        "https://factchecktools.googleapis.com/v1alpha1/claims:search",
        params={**params, "key": API_KEY}
    )
    r.raise_for_status()
    data = r.json()

    for item in data.get("claims", []):
        claim_text = item.get("text", "No title")  # try to fatch main  claim
        claim_date = item.get("claimDate") or datetime.now().isoformat()
        reviews = item.get("claimReview", [])

        if reviews:
            for review in reviews:  #  loop over ALL reviews
                article = {
                    "title": review.get("title", claim_text),# it review have it claim it on othersiwe take from main claim
                    "link": review.get("url", ""),
                    "published": claim_date,
                    "summary": review.get("textualRating", ""),
                    "source": review.get("publisher", {}).get("name", "Google Fact Check")
                }
                all_news.append(article)
        else:
            # erorr handle when empty claim
            article = {
                "title": claim_text,
                "link": "",
                "published": claim_date,
                "summary": "",
                "source": "Google Fact Check"
            }
            all_news.append(article)
   except requests.exceptions.RequestException as e:
        print(f"[API ERROR] Query '{query}' failed → {e}")


#  for all website that provide data by web scrapping

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def scrape_boom_articles(num_articles):
    url = "https://www.boomlive.in/fact-check"
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    articles = []
    links_seen = set()

    for a in soup.find_all("a", href=True):
        if "/fact-check/" in a.get("href") and a.text.strip():
            title = a.text.strip()
            link = a.get("href")

            if link.startswith("/"):
                link = "https://www.boomlive.in" + link

            # duplicates remove
            if link not in links_seen:
                links_seen.add(link)
                articles.append((title, link))

    # take only first n unique articles
    unique_articles = articles[:num_articles]

    results = []

    for title, link in unique_articles:
        try:
            time.sleep(1)  # sleep
            detail_page = requests.get(link, headers=headers)
            detail_soup = BeautifulSoup(detail_page.text, "html.parser")

            claim = detail_soup.find("h1").text.strip() if detail_soup.find("h1") else title
            first_p = detail_soup.find("p")
            verdict = first_p.text.strip() if first_p else ""

            #  Same JSON format as RSS feeds save
            article = {
                "title": claim,                          # h1 claim as title
                "link": link,
                "published": datetime.now().isoformat(),
                "summary": verdict[:300],
                "source": "BoomLive"
            }
            results.append(article)

        except Exception as e:
            print(f" Error scraping {link}: {e}")

    return results


all_news.extend(scrape_boom_articles(20))





    
import psycopg2

conn = psycopg2.connect(
    dbname="fake2fact",
    user="postgres",
    password="1084",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

for article in all_news:
    cur.execute("""
        INSERT INTO all_news (title, link, source, published,summary, content)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (
        article["title"],
        article["link"],
        article["source"],
        article["published"],
        article["summary"],
        json.dumps(article)
    ))

conn.commit()
cur.close()
conn.close()
print("✅ Articles stored in PostgreSQL")
    
