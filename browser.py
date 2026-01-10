from playwright.sync_api import Browser, sync_playwright
import os 
import time
import urllib.parse
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

SCREENSHOT_DIR = "screenshots"

def ensure_dirs():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

def open_page(url, timeout=15000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout)
        page.wait_for_load_state("networkidle")
        text = page.inner_text("body")
        browser.close()
        return text

def capture_screenshot(url, filename=None, timeout=15000):
    ensure_dirs()
    if filename is None:
        filename = f"{int(time.time())}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout)
        page.screenshot(path=path, full_page=True)
        browser.close()
    return path

def search_web(query, max_results=5, time_range="recent"):
    
    
    for attempt in range(3):
        try:
            search_query = query
            
            if attempt == 0 and time_range:
                if time_range == "recent":
                    search_query = f"{query} {datetime.now().year}"
                elif time_range == "day":
                    search_query = f"{query} today"
                elif time_range == "week":
                    search_query = f"{query} this week"
                elif time_range == "month":
                    search_query = f"{query} this month"
                elif time_range == "year":
                    search_query = f"{query} {datetime.now().year}"
            
            print(f"Attempt {attempt + 1}: Searching for '{search_query}'...")
            
            results = []
            
            ddgs = DDGS()
            search_results = list(ddgs.text(search_query, max_results=max_results))
            
            for result in search_results:
                if result:
                    results.append({
                        "title": result.get("title", "No title"),
                        "url": result.get("href", result.get("link", "")),
                        "snippet": result.get("body", result.get("snippet", "No description"))
                    })
            
            if results:
                print(f"✓ Found {len(results)} results")
                return results
                
            print(f"✗ No results on attempt {attempt + 1}")
            time.sleep(1)
                
        except Exception as e:
            print(f"✗ Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    print("⚠ All search attempts failed")
    return []