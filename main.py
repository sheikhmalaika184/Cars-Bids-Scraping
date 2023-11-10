import requests 
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import urllib.request
import pandas as pd

BASE_DIR = "" #give folder path here like "desktop/" always put "/" at the end of path

# starting a browser 
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument('--disable-blink-features=AutomationControlled')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

def make_request(url):
  try:
    driver.get(url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 2000)")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000)") 
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000)") 
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000)") 
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000)") 
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml') #convert the result into lxml
    return soup
  except Exception as e:
    print(e)

def get_cars_links(soup):
  try:
    ul_tag = soup.find("ul", class_ = "auctions-list past-auctions")
    li_tags = ul_tag.find_all("li", class_ ="auction-item")
    cars_links = []
    for tag in li_tags:
      try:
        a = tag.find("a", class_ ="hero")
        link = "https://carsandbids.com"+a['href']
        cars_links.append(link)
      except:
        continue
    return cars_links
  except Exception as e:
    print(e)

def creat_directory(name):
  try:
    path = BASE_DIR + name
    os.makedirs(path)
    os.makedirs(path+"/pictures")
  except FileExistsError:
    pass

def get_info(cars_links):
  for i in range(0,len(cars_links)):
    print(i)
    link = cars_links[i]
    driver.get(link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml') #convert the result into lxml

    # title 
    title_tag = soup.find("div", class_= "auction-title")
    car_title = title_tag.find("h1").text
    creat_directory(car_title)

    # price
    price_tag = soup.find("div", class_="row auction-bidbar")
    car_price = price_tag.find("li", class_="ended")
    car_price = car_price.find("span", class_="value").text

    # facts
    facts_tag = soup.find("div", class_="quick-facts")
    dl_tags = facts_tag.find_all("dl")
    dt_tags = []
    dd_tags = []
    for dl in dl_tags:
      dt_tags.extend(dl.find_all("dt"))
      dd_tags.extend(dl.find_all("dd"))
    
    # highlight
    highlights_tag = soup.find("div", class_="detail-section detail-highlights")
    highlights = highlights_tag.text.replace("Highlights","")

    # equipments 
    equipments_tag = soup.find("div",class_="detail-section detail-equipment")
    equipments = equipments_tag.find_all("li")

    #other items
    other_items_tag = soup.find("div",class_="detail-section detail-other_items")
    other_items = other_items_tag.find_all("li")

    # images
    #images_tag = soup.find("div", class_="row auction-photos")
    driver.execute_script("window.scrollTo(0, 400)") 
    time.sleep(5)
    images_tag = driver.find_element(By.XPATH, "//div[@class='row auction-photos']")
    all_images_tag = images_tag.find_element(By.XPATH, "//div[@class='all']")
    print(all_images_tag.text)
    all_images_tag.click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml') #convert the result into lxml
    images_tag = soup.find("div",class_="gallery-thumbs")
    images = images_tag.find_all("img")
    i = 1
    for image in images:
      src = image['src']
      src = src.replace("width=456","width=2080")
      urllib.request.urlretrieve(src, f"{BASE_DIR}{car_title}/pictures/image{i}.png")
      i = i + 1

    # writing text data
    dict_data = {'title':[car_title],'price':[car_price],'highlights':[highlights]}
    file = open(f"{BASE_DIR}{car_title}/information.txt", "w")
    file.write(car_title + "\n")
    file.write(car_price + "\n")
    file.write("\n")
    for f in range(0,len(dt_tags)):
      x = dd_tags[f].text.replace("Save","")
      file.write(f"{dt_tags[f].text}:{x} \n")
      dict_data[dt_tags[f].text] = [x]
    file.write("\n")
    file.write("Highlights\n")
    file.write(highlights+"\n")
    file.write("\n")
    file.write("Equipments\n")
    for e in equipments:
      file.write(f"{e.text} \n")
    file.write("\n")
    file.write("Other Items Included in Sale\n")
    for o in other_items:
      file.write(f"{o.text}\n")
    file.write("\n")
    file.write(link)
    file.close()
    print(car_title)
    print(car_price)
    for f in range(0,len(dt_tags)):
      print(dt_tags[f].text,": ",dd_tags[f].text.replace("Save",""))
    print(highlights)
    for e in equipments:
      print(e.text)
    for o in other_items:
      print(o.text)
    #print(cars_links[i])
    print("")
    # writing a csv file
    df = pd.DataFrame(dict_data)
    print(df)
    df.to_csv(f"{BASE_DIR}{car_title}/information.csv", index=False)

soup = make_request('https://carsandbids.com/past-auctions/?page=0')
cars_links = get_cars_links(soup)
print(len(cars_links))
get_info(cars_links)