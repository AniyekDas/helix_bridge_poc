import os
import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Folder containing JSON files
files_folder = "files"
pages_folder = "pages"

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
sitename = os.getenv('SITENAME')
instance_id = os.getenv('INSTANCE_ID')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Step 1: Go to dashboard
    page.goto(f"https://{sitename}/webbuilder/dashboard")

    # Step 2: Click the Webbuilder Login button and fill the login credentials
    page.click('xpath=//*[@id="app"]/div[1]/div[1]/div[1]/div/div[2]/a')

    page.fill('xpath=//*[@id="username"]', username)
    page.fill('xpath=//*[@id="password"]', password)
    page.press('xpath=//*[@id="password"]', "Enter")

    # Step 3: Navigate to Content > Files
    page.goto(f"https://{sitename}/builder/website/{instance_id}?panel=left-sidebar-settings--file-manager")
    page.wait_for_timeout(5000)

    # Step 4: Scan all JSON files in the folder and paste the found details in mentioned instance_id
    for file_name in os.listdir(files_folder):
        f_name = ""
        f_path = ""
        f_url = ""
        f_category = ""
        f_only_on_deploy = ""
        f_deploy_on = ""
        f_weight = ""
        f_pages = []

        index = 0 # needed for multiple entries in search result

        if file_name.endswith(".json"):
            file_path = os.path.join(files_folder, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                f_name = data["details"]["filename"]
                f_path = data["details"]["filepath"]
                f_url = data["details"]["url"]
                f_only_on_deploy = data["details"]["only_on_deployment"]
                f_deploy_on = data["details"]["deploy_on"]
                f_category = data["details"]["category"]
                f_weight = data["details"]["weight"]
                f_pages = data["details"]["pages"]
    
                # Convert the Variables to String
                f_path_str = str(f_path)
                f_url_str = str(f_url)
                f_only_on_deploy_str = str(f_only_on_deploy)
                f_deploy_on_str = str(f_deploy_on)
                f_category_str = str(f_category)
                f_weight_str = str(f_weight)

            # Search for file name
            search_box = page.locator('xpath=//*[@id="file-search-text-input"]')
            search_box.click()
            page.keyboard.press("Control+A")
            search_box.fill(f_name)
            search_box.press("Enter")
            page.wait_for_timeout(1000)

            # Check if file name appears in page
            if page.locator(f"text={f_name}").is_visible():
                rows = page.query_selector_all('table[data-v-7a2af82c] tbody tr')

                # Scan each row for the exact value from Table
                for i, row in enumerate(rows):
                    first_column = row.query_selector("td:nth-child(1)")
                    if first_column.inner_text().strip() == f_name:
                        index = i + 1
                
                # Click edit icon of the file
                page.locator(f'xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div/div[2]/table/tbody/tr[{index}]/td[7]/div/span[1]/a/i').click()
                page.wait_for_timeout(2000)

                # Paste the pages data in the file config
                for key, value in f_pages.items():
                    pages_count = len(f_pages)
                    if pages_count <= 1:
                        attach_page = page.locator('xpath=//*[@id="attachToAll"]')
                        attach_page.click()
                    else:
                        for page_path in os.listdir(pages_folder):
                            if page_path.endswith(".json"):
                                page_file_path = os.path.join(pages_folder, page_path)
                                with open(page_file_path, "r", encoding="utf-8") as f:
                                    page_data = json.load(f)
                                    p_title = page_data['settings']['title']
                                    p_uuid = page_data['settings']['uuid']
                                if key == p_uuid:
                                    page.locator('xpath=//*[@id="attachToIndividual"]').click() #click on Individial Pages Radio Button
                                    page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]').click()
                                    add_individual_pages = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]/input')
                                    add_individual_pages.fill(p_title)
                                    page.keyboard.press("Enter")
                                    page.wait_for_timeout(700)

                # Paste file details in field
                weight_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[2]/input')
                weight_field.click()
                page.keyboard.press("Control+A")
                weight_field.fill(f_weight_str)
                page.wait_for_timeout(1000)

                path_field = page.locator("input[name='filepath']")
                path_field.click()
                page.keyboard.press("Control+A")
                path_field.fill(f_path_str)
                page.wait_for_timeout(1000)

                if f_category_str != "":
                    category_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[3]/div/div[2]/span')
                    category_field.click()
                    page.wait_for_timeout(1000)
                    category_fill = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[3]/div/div[2]/input')
                    category_fill.fill(f_category_str)
                    page.wait_for_timeout(2000)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)

                # Click Save button
                page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[1]/div[2]/div[2]/button').click()

    browser.close()
