from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import csv

# Setup headless Chrome
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)

# Go to project list page
url = "https://rera.odisha.gov.in/projects/project-list"
driver.get(url)
time.sleep(5)

results = []
project_count = 6  # Number of projects you want to scrape

def extract_field(soup, label_text):
    try:
        labels = soup.find_all("label")
        for label in labels:
            if label.text.strip().lower() == label_text.strip().lower():
                strong = label.find_next("strong")
                if strong:
                    return strong.text.strip()
    except Exception as e:
        print(f"⚠️ Error extracting {label_text}: {e}")
    return "N/A"

# Loop through each project
for i in range(project_count):
    try:
        view_buttons = driver.find_elements(By.CLASS_NAME, "btn-primary")

        if i >= len(view_buttons):
            print(f"⚠️ Only found {len(view_buttons)} buttons, but index {i} requested.")
            break

        # Click project view button
        driver.execute_script("arguments[0].click();", view_buttons[i])
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract fields from Project Details tab
        rera_no = extract_field(soup, "RERA Regd. No.")
        project_name = extract_field(soup, "Project Name")

        # Switch to Promoter Details tab
        try:
            promoter_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Promoter Details')]")
            promoter_tab.click()
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')  # Refresh soup
        except Exception as e:
            print("⚠️ Could not switch to Promoter Details tab:", e)

        # Extract required promoter details
        promoter_name = extract_field(soup, "Company Name")
        promoter_address = extract_field(soup, "Registered Office Address")
        gst_no = extract_field(soup, "GST No.")

        # Store data
        results.append({
            "RERA Regd. No": rera_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Address of the Promoter": promoter_address,
            "GST No": gst_no
        })

        # Go back for next project
        driver.back()
        time.sleep(3)

    except StaleElementReferenceException as e:
        print(f"⚠️ Stale element error on project {i+1}: {e}")
    except WebDriverException as e:
        print(f"⚠️ WebDriver error on project {i+1}: {e}")

# Close browser
driver.quit()

# Print and save results
print("\n🎯 Extracted Project Info:\n")
for i, project in enumerate(results, 1):
    print(f"🔹 Project {i}")
    for key, value in project.items():
        print(f"{key}: {value}")
    print("-" * 50)

# Save to CSV
csv_filename = "rera_project_details.csv"
with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
    fieldnames = [
        "RERA Regd. No",
        "Project Name",
        "Promoter Name",
        "Address of the Promoter",
        "GST No"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for project in results:
        writer.writerow(project)

print(f"✅ Data successfully saved to '{csv_filename}'")
