from datetime import datetime, timedelta

from dateutil.parser import parse, ParserError
import pandas as pd
import requests as requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gd


scope =["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("scraper_credentials.json", scope)
client = gspread.authorize(creds)
sh = client.open_by_url('GOOGLE_WORKSHEET_URL').worksheet('GOOGLE_WORKSHEET_SHEET_NAME')

driver = webdriver.Firefox('PATH_TO_DRIVER_FILE')

def search_eventbrite(search_term):
    driver.get('https://www.eventbrite.co.uk/d/united-kingdom/"{}"/'.format(search_term))
    try:
        page_number = driver.find_element(by=By.XPATH, value='//li[@class="eds-pagination__navigation-minimal eds-l-mar-hor-3"]')
        page_string = page_number.get_attribute('innerHTML')
        pages = page_string.split()[-1]
    except NoSuchElementException:
        pages = '1'

    titles = []
    dates = []
    locations = []
    links = []

    for page in range(1, int(pages)+1):
        url = 'https://www.eventbrite.co.uk/d/united-kingdom/"{}"/?page={}'.format(search_term, page)
        response = requests.get(url, timeout=60)
        content = BeautifulSoup(response.content, "html.parser")
        events = content.findAll('div', attrs={"class": "search-event-card-wrapper"})
        for e in events:
            link = e.find('a', attrs={"class": "eds-event-card-content__action-link"})['href']
            title = e.find('div', attrs={"class": "eds-is-hidden-accessible"}).text
            datetime_string = e.find('div', attrs={"class": "eds-event-card-content__sub-title eds-text-color--primary-brand eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm"}).text
            try:
                if 'more events' in datetime_string:
                    if 'Tomorrow' in datetime_string:
                        date = parse(str(datetime.today().date() + timedelta(days=1)) + ' ' + datetime_string.split()[-5])
                    elif 'Today' in datetime_string:
                        date = parse(str(datetime.today().date()) + ' ' + datetime_string.split()[-5])
                    else:
                        string = datetime_string.split(' ')
                        date = parse(' '.join(string[:-4]))
                elif 'Tomorrow' in datetime_string:
                    date = parse(str(datetime.today().date() + timedelta(days=1)) + ' ' + datetime_string.split()[-1])
                elif 'Today' in datetime_string:
                    date = parse(str(datetime.today().date()) + ' ' + datetime_string.split()[-1])
                else:
                    date = parse(datetime_string)
            except ParserError:
                date = 'N/A'
            location = e.find('div', attrs={"data-subcontent-key": "location"}).text.split('•')[1]
            titles.append(title)
            locations.append(location)
            dates.append(date)
            links.append(link)
    return links, dates, locations, titles


def search_all_eventbrite():
    all_titles = []
    all_dates = []
    all_locations = []
    all_links = []
    search_terms = ['YOUR SEARCH TERMS HERE']
    for term in search_terms:
        all_results = search_eventbrite(term)
        all_links.extend(all_results[0])
        all_dates.extend(all_results[1])
        all_locations.extend(all_results[2])
        all_titles.extend(all_results[3])

    return all_titles, all_dates, all_links, all_locations


# search_all_eventbrite()