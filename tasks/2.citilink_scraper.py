import asyncio
import re
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def fetch_page_content(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_selector("div.app-catalog-1vans5j-StyledWrapper-StyledSnippetProductVerticalLayout", timeout=10000)
            last_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                try:
                    await page.wait_for_function("document.body.scrollHeight > " + str(last_height), timeout=5000)
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        logging.info("No more content loaded after scrolling.  Exiting scroll loop.")
                        break
                    last_height = new_height
                except PlaywrightTimeoutError:
                    break
            html_content = await page.content()
            await browser.close()
            return html_content
    except Exception as e:
        logging.error(f"Error fetching page with Playwright: {e}")
        return ""

async def get_products_data(html_content: str) -> list[dict] | None:
    soup = BeautifulSoup(html_content, "html.parser")
    product_class_regex = re.compile(r'e59n8xw0 app-catalog-.*StyledGridItem--StyledGridItem-GridItem--WrappedGridItem.*')
    product_items = soup.find_all('div', class_=product_class_regex)
    result = []
    for product_item in product_items:
        link_class_regex = re.compile(r'app-catalog-.*Anchor--Anchor-Anchor--StyledAnchor.*')
        link_item = product_item.find('a', class_=link_class_regex)
        if not link_item:
            logging.error("Cant get link for product")
            continue
        href = link_item.get('href')
        if not href or not 'product' in href:
            logging.error(f"Cant get link for product from block {href}")
            continue
        title = link_item.get_text().strip("Процессор ")
        brand = title.split()[0]
        model = title.strip(brand).split(',')[0].strip()
        price_class_regex = re.compile(r'app-catalog-.*StyledOrderInfoWrapper.*')
        price_item = product_item.find('div', class_=price_class_regex)
        if not price_item:
            logging.error("Cant get price for product")
            continue
        price = price_item.get_text().split("₽")[0].replace(" ", "")
        if "%" in price:
            price = price.split("%")[1]
        result.append({
            "brand": brand,
            "model": model,
            "price": price,
        })
    return result

async def main():
    url = "https://www.citilink.ru/catalog/processory/?sorting=price_desc"
    html_content = await fetch_page_content(url)
    if not html_content:
        logging.error("Failed to fetch page content.")
        return
    products = await get_products_data(html_content)
    if not products:
        logging.error("Cant extract products links")
        return
        

if __name__ == "__main__":
    asyncio.run(main())