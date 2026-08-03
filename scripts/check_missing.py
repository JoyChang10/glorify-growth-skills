import json
import time
import random
import cloudscraper
from bs4 import BeautifulSoup

# Initialize the cloudscraper instance to bypass 403 Forbidden blocks
scraper = cloudscraper.create_scraper()

# 1. Load your existing data
with open('sge_articles_sitemap.json', 'r', encoding='utf-8') as f:
    existing_articles = json.load(f)
    scraped_urls = {article['url'] for article in existing_articles}

print(f"Loaded {len(scraped_urls)} previously scraped articles.")

# 2. Get the full list of URLs from the sitemap index
index_url = 'https://www.socialgrowthengineers.com/sitemap.xml'
response = scraper.get(index_url)
print(f"Sitemap Status Code: {response.status_code}")
print(f"Sitemap Response: {response.text[:200]}")
soup = BeautifulSoup(response.text, 'xml')
sub_sitemaps = [loc.text for loc in soup.find_all('loc')]

all_sitemap_urls = []
for sitemap_url in sub_sitemaps:
    sub_resp = scraper.get(sitemap_url)
    sub_soup = BeautifulSoup(sub_resp.text, 'xml')
    all_sitemap_urls.extend([loc.text for loc in sub_soup.find_all('loc')])

# 3. Find the difference
missing_urls = [url for url in all_sitemap_urls if url not in scraped_urls]

print(f"Found {len(missing_urls)} missing URLs to scrape.")

if not missing_urls:
    print("Your dataset is complete. Nothing to scrape.")
else:
    new_articles = []
    for url in missing_urls:
        print(f"Scraping missing: {url}")
        try:
            # Add timeout to scraper
            page_resp = scraper.get(url, timeout=10)
            
            # 1. Log server rejections
            if page_resp.status_code != 200:
                print(f"Rejected: Code {page_resp.status_code} for {url}")
                continue
                
            page_soup = BeautifulSoup(page_resp.text, "html.parser")
            title = page_soup.find("h1").text.strip() if page_soup.find("h1") else "No Title"
            
            main_container = page_soup.find("article") or page_soup.find("main") or page_soup
            content = main_container.get_text(separator="\n\n", strip=True)
            
            # 2. Log empty content extractions
            if not content:
                print(f"Empty Content: No text found on {url}")
                
            if content:
                new_articles.append({
                    "url": url,
                    "title": title,
                    "content": content
                })
                
            # Randomize the delay between 1.5 and 3 seconds to avoid rate limits
            time.sleep(random.uniform(1.5, 3.0))
            
        except Exception as e:
            print(f"Network error: {url} - {e}")

    # Combine old data and new data
    all_articles = existing_articles + new_articles
    
    # Save back to the original file
    with open("sge_articles_sitemap.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=4, ensure_ascii=False)
        
    print(f"Added {len(new_articles)} missing articles. File updated.")