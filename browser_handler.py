"""
Browser automation handler using Playwright.
Handles JavaScript rendering and page interaction.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from config import settings

logger = logging.getLogger(__name__)


class BrowserHandler:
    """Handles headless browser operations for quiz pages."""

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def initialize(self) -> None:
        """Initialize Playwright and browser."""
        try:
            logger.info("Initializing Playwright browser...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")

    async def get_quiz_content(self, url: str) -> Dict[str, Any]:
        """
        Visit a quiz URL and extract the rendered content.

        Args:
            url: The quiz URL to visit

        Returns:
            Dict containing the quiz HTML, text content, and any extracted information
        """
        page: Optional[Page] = None
        try:
            logger.info(f"Navigating to quiz URL: {url}")
            page = await self.context.new_page()

            # Navigate to the URL
            await page.goto(url, wait_until='networkidle', timeout=settings.BROWSER_TIMEOUT)

            # Wait for potential JavaScript rendering
            await page.wait_for_timeout(2000)  # 2 seconds for JS execution

            # Extract all content
            html_content = await page.content()
            text_content = await page.inner_text('body')

            # Try to extract specific elements
            result_element = await page.query_selector('#result')
            result_text = await result_element.inner_text() if result_element else ""

            # Check for any download links
            download_links = await page.query_selector_all('a[href*="http"]')
            links = []
            for link in download_links:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                if href:
                    links.append({'url': href, 'text': text})

            # Take a screenshot for debugging
            screenshot_path = settings.TEMP_DIR / f"quiz_{hash(url)}.png"
            await page.screenshot(path=str(screenshot_path))

            logger.info(f"Successfully extracted content from {url}")

            return {
                'url': url,
                'html': html_content,
                'text': text_content,
                'result_text': result_text,
                'links': links,
                'screenshot': str(screenshot_path)
            }

        except Exception as e:
            logger.error(f"Error getting quiz content from {url}: {e}")
            raise
        finally:
            if page:
                await page.close()

    async def download_file(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a file from a URL.

        Args:
            url: The file URL to download
            filename: Optional custom filename

        Returns:
            Path to the downloaded file
        """
        page: Optional[Page] = None
        try:
            logger.info(f"Downloading file from: {url}")
            page = await self.context.new_page()

            # Set up download handler
            download_path = None
            async with page.expect_download() as download_info:
                await page.goto(url)
                download = await download_info.value

                # Determine filename
                if filename is None:
                    filename = download.suggested_filename or f"download_{hash(url)}"

                download_path = settings.DOWNLOADS_DIR / filename
                await download.save_as(str(download_path))

            logger.info(f"File downloaded to: {download_path}")
            return download_path

        except Exception as e:
            logger.error(f"Error downloading file from {url}: {e}")
            # Fallback: try direct download with requests
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        if filename is None:
                            filename = url.split('/')[-1] or f"download_{hash(url)}"
                        download_path = settings.DOWNLOADS_DIR / filename
                        with open(download_path, 'wb') as f:
                            f.write(await response.read())
                        logger.info(f"File downloaded via fallback to: {download_path}")
                        return download_path
            raise

        finally:
            if page:
                await page.close()
