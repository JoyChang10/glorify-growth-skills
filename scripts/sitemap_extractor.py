import json
import time
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 1. Fetch the main sitemap index
index_url = 'https://www.socialgrowthengineers.com/sitemap.xml'
response = requests.get(index_url, headers=headers)
soup = BeautifulSoup(response.text, 'xml')

# Find all sub-sitemap URLs
sub_sitemaps = [loc.text for loc in soup.find_all('loc')]
print(f"Found {len(sub_sitemaps)} sub-sitemaps.")

# 2. Fetch all actual page URLs from the sub-sitemaps
article_urls = []
for sitemap_url in sub_sitemaps:
    print(f"Reading sub-sitemap: {sitemap_url}")
    sub_resp = requests.get(sitemap_url, headers=headers)
    sub_soup = BeautifulSoup(sub_resp.text, 'xml')
    
    # Add all  tags from this sub-sitemap to our main list
    urls = [loc.text for loc in sub_soup.find_all('loc')]
    article_urls.extend(urls)
    time.sleep(1)  # 1-second delay to avoid blocking

print(f"Found {len(article_urls)} total URLs to scrape.")

# 3. Scrape the articles
articles_data = []

for url in article_urls:
    print(f"Scraping: {url}")
    try:
        page_resp = requests.get(url, headers=headers, timeout=10)
        if page_resp.status_code != 200:
            continue
            
        page_soup = BeautifulSoup(page_resp.text, "html.parser")
        
        title = page_soup.find("h1").text.strip() if page_soup.find("h1") else "No Title"
        
        # Extract paragraphs
        main_container = page_soup.find("article") or page_soup.find("main") or page_soup
        paragraphs = [p.text.strip() for p in main_container.find_all("p") if p.text.strip()]
        content = "\n\n".join(paragraphs)
        
        if content:
            articles_data.append({
                "url": url,
                "title": title,
                "content": content
            })
            
        time.sleep(1)
        
    except Exception as e:
        print(f"Failed to process {url}: {e}")

# 4. Save the data
with open("sge_articles_sitemap.json", "w", encoding="utf-8") as f:
    json.dump(articles_data, f, indent=4, ensure_ascii=False)

print(f"\nFinished! Saved {len(articles_data)} articles.")