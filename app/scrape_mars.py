# Importing Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

###########################################################################################################################################################
# Use a function called 'scrape' to execute all scraping code from Mission_to_Mars.ipynb and return one Python dictionary containing all scraped data
###########################################################################################################################################################

def scrape():

    # Initiating driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    mars_news_title, mars_news_p = NASA_mars_news(browser)

    # Running all scraping functions and storing in dictionary
    data = {
        "NASA_news_title": mars_news_title,
        "NASA_news_paragraph": mars_news_p,
        "JPL_featured_image": JPL_featured_image(browser),
        "USGS_hemispheres": USGS_hemispheres(browser),
        "Twitter_weather": twitter_weather(browser),
        "Mars_facts": mars_facts(),
        "last_updated": dt.datetime.now()
    }

    # Stopping webdriver and returning data
    browser.quit()
    return data


def NASA_mars_news(browser):
    NASA_url = "https://mars.nasa.gov/news/"
    browser.visit(NASA_url)

    # Get first list item and wait half a second if not immediately present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    try:
        slide_element = soup.select_one("ul.item_list li.slide")
        mars_news_title = slide_element.find("div", class_="content_title").get_text()
        mars_news_p = slide_element.find(
            "div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return mars_news_title, mars_news_p


def JPL_featured_image(browser):
    JPL_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(JPL_url)

    # Finding and click the 'full image' button
    full_image_button = browser.find_by_id("full_image")
    full_image_button.click()

    # Finding the 'more info' button and click that
    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info_button = browser.find_link_by_partial_text("more info")
    more_info_button.click()

    # Parsing the resulting html with soup
    html = browser.html
    featured_img_soup = BeautifulSoup(html, "html.parser")

    # Find the relative image url
    featured_img = featured_img_soup.select_one("figure.lede a img")

    try:
        featured_img_url_rel = featured_img.get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    featured_img_url = f"https://www.jpl.nasa.gov{featured_img_url_rel}"

    return featured_img_url


def USGS_hemispheres(browser):

    # A way to break up long strings
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    # Click the link, find the sample anchor, return the href
    hemisphere_image_urls = []
    for i in range(4):

        # Find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()

        hemi_data = scrape_hemisphere(browser.html)

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemi_data)

        # Finally, we navigate backwards
        browser.back()

    return hemisphere_image_urls


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    # First, find a tweet with the data-name `Mars Weather`
    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = weather_soup.find("div", attrs=tweet_attrs)

    # Next, search within the tweet for the p tag containing the tweet text
    mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def scrape_hemisphere(html_text):

    # Soupify the html text
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # Try to get href and text except if error.
    try:
        title_element = hemi_soup.find("h2", class_="title").get_text()
        img_sample_element = hemi_soup.find("a", text="Sample").get("href")

    except AttributeError:

        # Image error returns None for better front-end handling
        title_element = None
        sample_element = None

    hemisphere = {
        "hemi_title": title_element,
        "hemi_img_url": img_sample_element
    }

    return hemisphere


def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
