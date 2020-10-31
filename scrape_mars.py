from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


def hemisphere_image_urls(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []

    links = browser.find_by_css("a.product-item h3")

    for x in range(len(links)):
        hemisphere = {}
        browser.find_by_css("a.product-item h3")[x].click()
        element = browser.links.find_by_text('Sample').first
        hemisphere['img_url'] = element['href']
        hemisphere['title'] = browser.find_by_css('h2.title').text
        hemisphere_image_urls.append(hemisphere)
        browser.back()
    
    print(hemisphere_image_urls)
    return 
    
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': '/Users/ChairezFamily/Documents/chromedriver'}
    browser = Browser('chrome', **executable_path)

    first_title, first_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": first_title,
        "news_paragraph": first_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    mars_news_soup = soup(html, 'html.parser')


    try:
        first_title = mars_news_soup.find("div", class_="content_title").get_text()
        first_paragraph = mars_news_soup.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return first_title, first_paragraph


def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")

if __name__ == "__main__":

    print(scrape_all())