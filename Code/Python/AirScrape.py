from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from bs4 import BeautifulSoup
from io import StringIO

# Initialize the Selenium WebDriver
driver = webdriver.Chrome()
driver.get("https://www.transtats.bts.gov/Data_Elements.aspx?Qn6n=F")
link_destination = driver.find_element(By.CSS_SELECTOR, "#Link_Destination")
link_destination.click()

load_factor_link = driver.find_element(By.CSS_SELECTOR, "#Link_RPM")
load_factor_link.click()

# Initialize a list to collect the DataFrames
all_airport_data = []

# Select the carrier dropdown and set it to the first option (assumed to be correct here)
carrier_select = Select(driver.find_element(By.ID, "CarrierList"))
carrier_select.select_by_index(0)  # Adjust as necessary for your carrier choice

# Select the airport dropdown element
airport_select = Select(driver.find_element(By.ID, "AirportList"))

# Loop through each option in the airport dropdown, starting from index 2
for index in range(2, len(airport_select.options)):
    # Re-locate the airport dropdown to avoid stale element issues
    airport_select = Select(driver.find_element(By.ID, "AirportList"))

    # Get the airport name
    airport_name = airport_select.options[index].text

    # Check if the airport name matches your conditions
    if "International" in airport_name or "PR" in airport_name or 2 <= index <= 32:
        # Select the current airport by index
        airport_select.select_by_index(index)

        # Submit the form to load data for the selected airport
        submit_button = driver.find_element(By.NAME, "Submit")
        submit_button.click()

        # Wait for the table to load (adjust the delay as needed)
        time.sleep(5)

        # Parse the page source with BeautifulSoup to locate the table
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", {"id": "GridView1"})  # Locate table with id 'GridView1'

        try:

            # Convert the table HTML to a DataFrame using StringIO to avoid the warning
            df = pd.read_html(StringIO(str(table)))[0]

            # Clean up the DataFrame
            df["Airport Name"] = airport_name  # Add a new column with the airport name
            df = df.drop(df.columns[[2, 3]], axis=1)  # Drop columns at index 2 and 3
            second_to_last_col = df.columns[-2]
            df = df.rename(columns={second_to_last_col: "Revenue Passenger Miles"})  # Rename second-to-last column to "Flights"
            df = df[~df["Month"].str.contains("TOTAL", case=False, na=False)]  # Remove rows where "Month" contains "TOTAL"

            # Append the cleaned DataFrame to the list
            all_airport_data.append(df)
        except ValueError:
            print(f"No tables found for airport: {airport_name}. Skipping.")

# Concatenate all DataFrames into a single DataFrame
final_df = pd.concat(all_airport_data, ignore_index=True)

# Export the concatenated DataFrame to a CSV file
final_df.to_csv("RevenuePassengerMiles.csv", index=False)

# Close the WebDriver
# driver.quit()

# Confirm the file was created and show the first few rows
print("CSV file created successfully.")
print(final_df.head())
