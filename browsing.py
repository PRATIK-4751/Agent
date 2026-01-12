import asyncio
from playwright.async_api import async_playwright
import os
from text import TextResponseHandler
import base64
from datetime import datetime

class WebBrowser:
    def __init__(self):
        self.handler = TextResponseHandler()
        self.browser = None
        self.page = None
    
    async def start_browser(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
    
    async def close_browser(self):
        if self.browser:
            await self.browser.close()
    
    async def take_screenshot(self, path=None):
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshot_{timestamp}.png"
        
        await self.page.screenshot(path=path, full_page=True)
        return path
    
    async def capture_and_process(self, url, query):
        if not self.browser:
            await self.start_browser()
        
        try:
            await self.page.goto(url, timeout=30000)
            await self.page.wait_for_load_state('networkidle')
            screenshot_path = await self.take_screenshot()
            content = await self.page.content()
            page_text = await self.page.evaluate('''() => {
                Array.from(document.querySelectorAll('script, style, nav, footer')).forEach(el => el.remove());
                return document.body.innerText;
            }''')
            
            if len(page_text) > 2000:
                page_text = page_text[:2000] + "... [truncated]"
            
            prompt = f"""
            URL: {url}
            Page Content: {page_text}
            
            User Query: {query}
            
            Please analyze the webpage content and respond to the user's query based on the information found on the page.
            """
            
            response = self.handler.get_response(prompt, use_local=True)
            
            with open(screenshot_path, "rb") as img_file:
                screenshot_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            return {
                "response": response,
                "screenshot_path": screenshot_path,
                "screenshot_base64": screenshot_base64,
                "url": url,
                "page_text": page_text
            }
        
        except Exception as e:
            error_msg = f"Error browsing {url}: {str(e)}"
            error_prompt = f"The web browsing request failed with error: {error_msg}. Please inform the user about this issue."
            response = self.handler.get_response(error_prompt, use_local=True)
            
            return {
                "response": response,
                "screenshot_path": None,
                "screenshot_base64": None,
                "url": url,
                "page_text": None,
                "error": error_msg
            }

async def main():
    browser = WebBrowser()
    try:
        result = await browser.capture_and_process("https://www.python.org", "What is Python?")
        print("Response:", result["response"])
        print("Screenshot saved to:", result["screenshot_path"])
    finally:
        await browser.close_browser()

if __name__ == "__main__":
    asyncio.run(main())