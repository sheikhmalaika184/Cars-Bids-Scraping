import os
import time
import urllib.request
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = Path("")  # Example: Path("/Users/myuser/Desktop/")

# ---------- Browser Setup ----------
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# User agent for urllib
opener = urllib.request.build_opener()
opener.addheaders = [
    ('User-Agent',
     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')
]
urllib.request.install_opener(opener)


# ---------- Utility Functions ----------
def scroll_slow(times=4, pixels=2000, delay=1.5):
    """Smooth repeated scrolling to load dynamic content."""
    for _ in range(times):
        driver.execute_script(f"window.scrollTo(0, {pixels})")
        time.sleep(delay)


def make_request(url):
    try:
        driver.get(url)
        scroll_slow(5)
        return BeautifulSoup(driver.page_source, "lxml")
    except Exception as e:
        print("Error in make_request:", e)
        return None


def create_directory(folder_name):
    try:
        path = BASE_DIR / folder_name
        (path / "pictures").mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        print("Directory creation error:", e)
        return None


# ---------- Extract Cars Links ----------
def get_cars_links(soup):
    try:
        ul = soup.find("ul", class_="auctions-list past-auctions")
        li_tags = ul.find_all("li", class_="auction-item")

        links = [
            "https://carsandbids.com" + li.find("a", class_="hero")['href']
            for li in li_tags if li.find("a", class_="hero")
        ]
        return links

    except Exception as e:
        print("Error extracting car links:", e)
        return []


# ---------- Extract Details of Each Car ----------
def get_car_details(url):
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "auction-title"))
    )

    soup = BeautifulSoup(driver.page_source, "lxml")

    # title
    title = soup.find("div", class_="auction-title").find("h1").text.strip()
    car_dir = create_directory(title)

    # price
    price = (
        soup.find("div", class_="row auction-bidbar")
        .find("li", class_="ended")
        .find("span", class_="value").text.strip()
    )

    # facts
    facts_section = soup.find("div", class_="quick-facts")
    dl_tags = facts_section.find_all("dl")

    facts = {}
    for dl in dl_tags:
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            facts[dt.text.strip()] = dd.text.replace("Save", "").strip()

    # highlights
    highlights = (
        soup.find("div", class_="detail-section detail-highlights")
        .text.replace("Highlights", "").strip()
    )

    # equipment
    equipments = [li.text.strip() for li in soup.find(
        "div", class_="detail-section detail-equipment").find_all("li")]

    # other items
    other_items = [li.text.strip() for li in soup.find(
        "div", class_="detail-section detail-other_items").find_all("li")]

    # ---------- Download Images ----------
    scroll_slow(2, 500)

    try:
        full_gallery_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='all']"))
        )
        full_gallery_btn.click()
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "lxml")
        images = soup.find("div", class_="gallery-thumbs").find_all("img")

        for i, img in enumerate(images, start=1):
            src = img['src'].replace("width=456", "width=2080")
            img_path = car_dir / "pictures" / f"image{i}.png"
            urllib.request.urlretrieve(src, img_path)

    except Exception as e:
        print(f"Image extraction failed for {title}: {e}")

    # ---------- Save Text ----------
    info_file = car_dir / "information.txt"
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(title + "\n")
        f.write("Price: " + price + "\n\n")

        for k, v in facts.items():
            f.write(f"{k}: {v}\n")

        f.write("\nHighlights:\n" + highlights + "\n\n")

        f.write("Equipments:\n")
        for e in equipments:
            f.write(e + "\n")

        f.write("\nOther Items Included:\n")
        for o in other_items:
            f.write(o + "\n")

        f.write("\nLink: " + url)

    # ---------- Save CSV ----------
    df = pd.DataFrame([{**{"title": title, "price": price, "highlights": highlights}, **facts}])
    df.to_csv(car_dir / "information.csv", index=False)

    return title


# ---------- Main ----------
if __name__ == "__main__":
    soup = make_request("https://carsandbids.com/past-auctions/?page=0")
    car_links = get_cars_links(soup)

    print("Total Cars Found:", len(car_links))

    # process first 2 cars → change to len(car_links)
    for link in car_links[:len(car_links)]:
        print("Scraping:", link)
        title = get_car_details(link)
        print("Done:", title)
        print("-" * 40)
