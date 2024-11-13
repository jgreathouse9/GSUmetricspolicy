import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


# Function to retrieve all international airport URLs
def get_international_airport_urls():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=chrome_options)
    final_urls = []

    try:
        driver.get("https://www.transtats.bts.gov/airports.asp?20=E")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(3) > td:nth-child(3) > a"))
        )

        link = driver.find_element(By.CSS_SELECTOR,
                                   "body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(3) > td:nth-child(3) > a")
        link.click()

        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)

        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))

        all_links = driver.find_elements(By.TAG_NAME, "a")
        filter_strings = ["International", "LaGuardia", "VI:", "TT:", "PR:", "HI:"]

        filtered_links = [
            link.get_attribute("href")
            for link in all_links
            if any(f_string in link.text for f_string in filter_strings)
        ]

        base_url = "https://www.transtats.bts.gov/"
        for href in filtered_links:
            if href.startswith("javascript:window_Close('"):
                relative_url = href[len("javascript:window_Close('"):-2]
                final_url = base_url + relative_url.rstrip('%2')
                final_urls.append(final_url)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return final_urls


# Function to scrape data from a single URL
def scrape_airport_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=chrome_options)
    data = []

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#End_YearMonth')))

        dropdown_element = driver.find_element(By.CSS_SELECTOR, '#End_YearMonth')
        driver.execute_script("arguments[0].scrollIntoView();", dropdown_element)
        dropdown = Select(dropdown_element)

        for i in range(len(dropdown.options)):
            dropdown.select_by_index(i)

            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(4) > button')
            ))

            submit_button = driver.find_element(By.CSS_SELECTOR,
                                                'body > table > tbody > tr > td > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(4) > button')
            driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            submit_button.click()

            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#End_YearMonth')))
            dropdown_element = driver.find_element(By.CSS_SELECTOR, '#End_YearMonth')
            dropdown = Select(dropdown_element)

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            datastring = 'Freight/Mail (lb.) (Scheduled and Non-Scheduled)'

            freight_mail_header = soup.find('td', string=datastring)
            airport_name = soup.select_one(
                'body > table > tbody > tr > td > table:nth-child(2) > tbody > tr > th').text.strip()

            if freight_mail_header:
                freight_mail_row = freight_mail_header.find_parent('tr').find_next_sibling('tr')
                freight_mail_value = freight_mail_row.find_all('td')[2].text.strip()
                selected_month_year = dropdown.options[i].text.strip()

                data.append({
                    'airport': airport_name,
                    'month_year': selected_month_year,
                    'freight_mail_value': freight_mail_value
                })
        print(f"{airport_name} is completed")

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    finally:
        driver.quit()

    return data


# Function to scrape multiple URLs in parallel
def scrape_all_airports(urls):
    all_data = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(scrape_airport_data, url) for url in urls]

        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    all_data.extend(result)
            except Exception as e:
                print(f"Error in future: {e}")

    return all_data


# Main code
airport_urls = get_international_airport_urls()
data = scrape_all_airports(airport_urls)

df = pd.DataFrame(data)
df.to_csv('cargo_data_parallel.csv', index=False)
print(df.head())
