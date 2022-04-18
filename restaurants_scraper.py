import csv
import sys
import time

# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))

# default path to file to store data
path_to_file = "/Users/gius/Desktop/reviews.csv"

# default number of scraped pages
num_page = 10

# default tripadvisor website of restaurant
url = "https://www.tripadvisor.com/Restaurant_Review-g60763-d802686-Reviews-Hard_Rock_Cafe-New_York_City_New_York.html"

# if you pass the inputs in the command line
if (len(sys.argv) == 4):
    path_to_file = sys.argv[1]
    num_page = int(sys.argv[2])
    url = sys.argv[3]

# Import the webdriver
# driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)
time.sleep(2)
cookies = driver.find_element_by_id("onetrust-accept-btn-handler")
cookies.click()

# Open the file to save the review
csvFile = open(path_to_file, 'a', encoding="utf-8")
csvWriter = csv.writer(csvFile)

# change the value inside the range to save more or less reviews
for i in range(0, num_page):
    
    # expand the review 
    time.sleep(2)
    button = driver.find_element_by_xpath("//span[@class='taLnk ulBlueLinks']")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    container = driver.find_elements_by_xpath(".//div[@class='review-container']")
    print(f"Found {len(container)} reviews on page {i}.")

    for j in range(len(container)):

        title = container[j].find_element_by_xpath(".//span[@class='noQuotes']").text
        date = container[j].find_element_by_xpath(".//span[contains(@class, 'ratingDate')]").get_attribute("title")
        rating = container[j].find_element_by_xpath(".//span[contains(@class, 'ui_bubble_rating bubble_')]").get_attribute("class").split("_")[3]
        review = container[j].find_element_by_xpath(".//p[@class='partial_entry']").text.replace("\n", " ")

        csvWriter.writerow([date, rating, title, review]) 

    # change the page
    driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()

driver.close()
