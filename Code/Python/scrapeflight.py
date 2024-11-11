import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

def run_scraping_for_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    df = pd.DataFrame()

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "forthdiv"))
        )
        driver.execute_script("document.getElementById('forthdiv').classList.remove('hidden');")
        time.sleep(2)

        th_element = driver.find_element(By.CSS_SELECTOR, "body > table > tbody > tr > td > table:nth-child(2) > tbody > tr > th")
        airport_full_name = th_element.text
        airport_code = re.search(r'\((.*?)\)', airport_full_name).group(1) if airport_full_name else None

        soup = BeautifulSoup(driver.page_source, "html.parser")
        airport_dropdown = soup.select_one("#Airport")
        selected_option = airport_dropdown.find("option", selected=True).text if airport_dropdown else "Unknown Airport"

        dt_elements = soup.select("div#forthdiv dt")

        # Step 1: Organize data by date
        date_data = {}
        for dt in dt_elements:
            text = dt.get_text()
            if "Date:" in text:
                # Extract the date
                date = text.split(";")[0].split(":")[1].strip()

                # Initialize the date dictionary if not already created
                if date not in date_data:
                    date_data[date] = {'Date': date, 'Airport': selected_option, 'Airport Code': airport_code}

                # Extract delay metrics based on keywords in text
                if "Airport Delay %" in text:
                    date_data[date]['Airport Delay %'] = float(text.split("Airport Delay %:")[1].replace('%', '').strip())
                elif "Airport Average Delay" in text:
                    date_data[date]['Delay Minutes'] = float(text.split("Airport Average Delay:")[1].replace('minutes', '').strip())

        # Step 2: Convert collected data into a list of dictionaries
        parsed_data = [data for data in date_data.values()]
        # Step 3: Convert parsed data into a DataFrame
        df = pd.DataFrame(parsed_data)
        print(f"{airport_code} finished.")

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")

    finally:
        driver.quit()

    return df




def get_international_airport_urls():
    """
    This function scrapes the international airport URLs from the main page
    and returns a list of URLs that contain "International," "LaGuardia,"
    or any of the specified strings ("VI:", "TT:", "PR:", "HI:").
    """
    # Configure the Chrome WebDriver with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows OS only
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    final_urls = []

    try:
        # Navigate to the original URL
        driver.get("https://www.transtats.bts.gov/airports.asp?20=E")

        # Wait for the element to be clickable using the provided CSS selector
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(3) > td:nth-child(3) > a"))
        )

        # Locate the link and click it to open a new window
        link = driver.find_element(By.CSS_SELECTOR,
                                   "body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(3) > td:nth-child(3) > a")
        link.click()

        # Wait for the new window to open (ensure the number of windows becomes 2)
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        # Switch to the new window
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[1])  # Switch to the new window

        # Optional: wait for a bit to ensure the new window is fully loaded
        time.sleep(2)

        # Wait for the links to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )

        # Retrieve all <a> elements
        all_links = driver.find_elements(By.TAG_NAME, "a")

        # Filter the links based on the specified criteria
        filter_strings = ["International", "LaGuardia", "VI:", "TT:", "PR:", "HI:"]
        filtered_links = [
            link.get_attribute("href")
            for link in all_links
            if any(f_string in link.text for f_string in filter_strings)
        ]

        # Extract the actual URLs from the javascript links
        base_url = "https://www.transtats.bts.gov/"

        for href in filtered_links:
            if href.startswith("javascript:window_Close('"):
                # Extract the part of the href after 'javascript:window_Close(' and before the closing ')'
                relative_url = href[len("javascript:window_Close('"):-2]

                # Remove any trailing unwanted characters (like '%2')
                final_url = base_url + relative_url
                final_url = final_url.rstrip('%2')  # Remove the trailing "%2"

                final_urls.append(final_url)

    except Exception as e:
        print(f"An error occurred.")

    finally:
        # Close the WebDriver
        driver.quit()

    return final_urls


def scrape_all_airports():
    """
    This function loops through all international airport URLs, scrapes the data,
    and appends the results to a master DataFrame. Finally, saves the DataFrame to a CSV file.
    """
    urls = get_international_airport_urls()
    all_data = pd.DataFrame()

    for url in urls:
        df = run_scraping_for_url(url)
        all_data = pd.concat([all_data, df], ignore_index=True)

    all_data.to_csv('airport_delays.csv', index=False)
    print("Data has been saved to 'airport_delays.csv'.")

scrape_all_airports()
