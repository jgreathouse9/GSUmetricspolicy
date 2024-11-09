import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def run_scraping_for_url(url):
    """
    This function takes a URL, scrapes the airport data, and returns a DataFrame
    with the airport data (Date, Delay, Airport).
    """
    # Configure the Chrome WebDriver with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Runs Chrome in headless mode.
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows OS only
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=chrome_options)
    df = pd.DataFrame()  # Initialize empty DataFrame

    try:
        # Navigate to the given URL
        driver.get(url)

        # Wait for the 'forthdiv' element to load (indicating the page has loaded)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "forthdiv"))
        )

        # Ensure the 'forthdiv' is visible by removing the 'hidden' class
        driver.execute_script("document.getElementById('forthdiv').classList.remove('hidden');")

        # Wait a brief moment to ensure the 'forthdiv' content is visible
        time.sleep(2)

        # Retrieve all <dt> elements within 'forthdiv'
        dt_elements = driver.find_elements(By.TAG_NAME, "dt")

        # Get the selected airport from the dropdown
        airport_dropdown = driver.find_element(By.CSS_SELECTOR, "#Airport")
        selected_option = airport_dropdown.find_element(By.CSS_SELECTOR, "option:checked").text

        # Filter and parse the data into a structured list (Date and Delay)
        parsed_data = [
            {
                'Date': dt.text.split(';')[0].split(':')[1].strip(),
                'Delay (minutes)': float(dt.text.split(';')[1].split(':')[1].replace('minutes', '').strip()),
                'Airport': selected_option
            }
            for dt in dt_elements if "minute" in dt.text and "Airport" in dt.text
        ]

        # Create a DataFrame directly from the parsed data
        df = pd.DataFrame(parsed_data)

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    # Return the DataFrame containing the scraped data
    return df


def get_international_airport_urls():
    """
    This function scrapes the international airport URLs from the main page
    and returns a list of URLs.
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

        # Filter the links based on the text containing "International" or "LaGuardia"
        filtered_links = [
            link.get_attribute("href")
            for link in all_links
            if "International" in link.text or "LaGuardia" in link.text
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
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    # Return the list of final URLs
    return final_urls


def scrape_all_airports():
    """
    This function loops through all international airport URLs, scrapes the data,
    and appends the results to a master DataFrame.
    Finally, saves the DataFrame to a CSV file.
    """
    # Get all international airport URLs
    urls = get_international_airport_urls()

    # Initialize an empty DataFrame to hold all the scraped data
    all_data = pd.DataFrame()

    # Loop through each URL and scrape data
    for url in urls:
        print(f"Scraping data from: {url}")
        df = run_scraping_for_url(url)  # Scrape data from the URL

        # Append the new data to the master DataFrame
        all_data = pd.concat([all_data, df], ignore_index=True)

    # Save the final DataFrame to a CSV file
    all_data.to_csv('airport_delays.csv', index=False)
    print("Data has been saved to 'airport_delays.csv'.")


# Example usage:
# This will scrape data from all international airport URLs and save it to a CSV file
scrape_all_airports()
