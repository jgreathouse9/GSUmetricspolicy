from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import StringIO
import pandas as pd

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the URL
url = "https://www.transtats.bts.gov/averagefare/"
driver.get(url)

# Initialize an empty list to store DataFrames
df_list = []

# Loop over the years (2000 to 2001)
for year in range(2000, 2024):
    # Wait for the year dropdown to be visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#dlstYear")))

    # Select the year dynamically based on the loop
    year_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#dlstYear"))
    year_dropdown.select_by_visible_text(str(year))

    # Loop through the quarters (Q1, Q2, Q3, Q4) starting from the second element (Q1)
    quarter_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#dlstQuarter"))
    for quarter_index in range(1, len(quarter_dropdown.options)):  # Start from 1 to skip "Annual"
        # Wait for the quarter dropdown to be visible after selecting the year
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#dlstQuarter")))

        # Select the quarter dynamically based on the loop
        quarter_dropdown.select_by_index(quarter_index)  # Use quarter_index directly

        # Click the submit button
        submit_button = driver.find_element(By.CSS_SELECTOR, "#btnSubmit")
        submit_button.click()

        # Wait for the page to reload and for the dropdowns to become visible again
        WebDriverWait(driver, 10).until(EC.staleness_of(submit_button))  # Ensure the submit button is no longer present
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#dlstQuarter")))

        # Re-locate the dropdown elements after the reload
        year_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#dlstYear"))
        quarter_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#dlstQuarter"))

        # Print the selected year and quarter
        quart = quarter_dropdown.options[quarter_index].text

        # Wait for the table to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Get the table and read it into a DataFrame
        table = driver.find_element(By.TAG_NAME, "table")
        table_html = StringIO(table.get_attribute('outerHTML'))
        df = pd.read_html(table_html)[0]

        # Find the header row index for "City Name"
        header_row_index = df[df.iloc[:, 2].astype(str).str.contains("City Name", na=False)].index[0]

        # Set the rows after the header row and reset the index
        df = df.iloc[header_row_index:].reset_index(drop=True)
        df.columns = df.iloc[0]  # Set header row
        df = df[1:]  # Drop the first row now that it is the header

        # Remove "National Average" rows
        national_avg_index = df[
            df.apply(lambda row: row.astype(str).str.contains("National Average", case=False)).any(axis=1)
        ].index
        if not national_avg_index.empty:
            df = df.loc[:national_avg_index[0] - 1].reset_index(drop=True)

        # Clean up columns by removing unnecessary ones
        df = df.drop(df.columns[[0]].tolist() + df.columns[-3:].tolist(), axis=1)

        # Add the year and quarter to the DataFrame
        df['Year'] = year
        df['Quarter'] = quart

        # Append the DataFrame for this quarter
        df_list.append(df)

# Close the browser once done
driver.quit()

# Concatenate all DataFrames in the list into a final DataFrame
final_df = pd.concat(df_list, ignore_index=True)

final_df.to_csv('fare_data.csv', index=False)
