# Cars-Bids-Scraping
**Automated scraper for Cars & Bids — past auction listings**

This project scrapes past auction listings from https://carsandbids.com/past-auctions/ and saves structured car data (title, price, specs, images, etc.) locally for analysis or archiving.

---

## Key features

- Scrapes all past-auction car listings from Cars & Bids.
- Extracts structured fields for each car:
  - Title, Price, Highlights, Make, Model, Mileage, VIN, Title Status, Location, Seller, Engine, Drivetrain, Transmission, Body Style, Exterior Color, Interior Color, Year, Seller Type, Pictures
- Creates a folder per car, saves:
  - `information.csv` (tabular record)
  - `information.txt` (readable summary)
  - `pictures/` (downloaded images)
- Built with a focus on reliability, reusability and clear logging.

---

## Output structure

After running the scraper, each car will have its own folder:
output/
- ├─ 1991-Ford-Taurus-SHO-JT12345/
- │ ├─ information.csv
- │ ├─ information.txt
- │ └─ pictures/
- │  ├─ 0.jpg
- │  └─ 1.jpg

---

## Installation Steps
1. Clone the repo and install dependencies:
2. git clone https://github.com/sheikhmalaika184/Cars-Bids-Scraping.git
3. cd Cars-Bids-Scraping
4. pip install -r requirements.txt
5. Run the scraper: python main.py


