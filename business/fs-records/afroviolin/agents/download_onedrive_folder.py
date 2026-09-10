#!/usr/bin/env python3
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    # The OneDrive shared file URL
    url = "https://1drv.ms/u/c/29cfdba9cff0b72c/IQCRGx6dPDOTRbtHoaB3HzJAAf1kUZdcrxXZ6Sbvjzh-2Io?e=iqiuGH"
    output_path = "/data/workspace/onedrive_download.zip"
    
    print(f"Launching Playwright to visit OneDrive shared link: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set a realistic user agent and window size
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        page = context.new_page()
        
        # Navigate and wait for loading
        page.goto(url)
        print("Waiting for page to load and render completely...")
        page.wait_for_timeout(8000)
        
        # Take a screenshot to verify what it sees (saves to /data/workspace/onedrive_view.png)
        page.screenshot(path="/data/workspace/onedrive_view.png")
        print("Saved render screenshot to /data/workspace/onedrive_view.png")
        
        # Try to locate the Download button and click it
        download_button_selectors = [
            'button:has-text("Download")',
            '[data-automationid="downloadButton"]',
            'a:has-text("Download")',
            'button[title="Download"]',
            '[aria-label="Download"]'
        ]
        
        clicked = False
        for selector in download_button_selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0:
                    print(f"Found download locator: {selector}")
                    with page.expect_download(timeout=30000) as download_info:
                        locator.first.click()
                    download = download_info.value
                    download.save_as(output_path)
                    print(f"✓ Downloaded successfully to {output_path} ({os.path.getsize(output_path)} bytes)!")
                    clicked = True
                    break
            except Exception as e:
                print(f"Locator {selector} failed or timed out: {e}")
                
        if not clicked:
            print("Failed to trigger download via button selectors. Inspecting page links/elements...")
            # Dump page source of body to logs/page_body.txt for debugging
            with open("/data/workspace/onedrive_page_body.txt", "w") as f:
                f.write(page.content())
            print("Dumped page content to /data/workspace/onedrive_page_body.txt")

        browser.close()

if __name__ == "__main__":
    import os
    main()
