import os
import json
from playwright.sync_api import sync_playwright, TimeoutError
from dotenv import load_dotenv
import csv
import time

def create_block(page, b_title, b_description, b_category, b_protected, b_files, b_auto_attach, b_auto_attach_location, b_auto_attach_exceptions, b_auto_attach_to_error_pages, b_html, b_css):
    # Fill title
    b_title_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/div[1]/input')
    b_title_field.click()
    page.keyboard.press("Control+A")
    b_title_field.fill(b_title)
    page.wait_for_timeout(1000)

    # Fill Description
    b_description_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/input')
    b_description_field.click()
    page.keyboard.press("Control+A")
    b_description_field.fill(b_description)
    page.wait_for_timeout(1000)

    # Fill category
    page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/div[3]/div/div[2]').click()
    b_category_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[1]/div[3]/div/div[2]/input')
    b_category_field.fill(b_category)
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)

    # If protected, perform extended logic
    if b_protected:
        page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[2]/div/label/input').click()
        page.wait_for_timeout(1000)

        if isinstance(b_files, list) and b_files:
            for file_value in b_files:
                page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/section/section/div/div[3]').click()
                file_input = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/section/section/div/div[3]/input')
                file_input.fill(file_value)
                page.keyboard.press("Enter")
                page.wait_for_timeout(1000)

        if b_auto_attach:
            page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/label/input').click()
            page.wait_for_timeout(1000)

            if b_auto_attach_location:
                location_select = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[2]/div[3]/select')
                options = location_select.locator('option').all()
                for option in options:
                    option_text = option.text_content()
                    if option_text.strip() == b_auto_attach_location.strip():
                        option.click()
                        page.wait_for_timeout(1000)
                        break

            if isinstance(b_auto_attach_exceptions, list) and b_auto_attach_exceptions:
                exception_container = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[2]/div[4]/div/div[2]')
                page.wait_for_timeout(1000)
                for exception in b_auto_attach_exceptions:
                    exception_container.click()
                    exception_input = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div/div[2]/div/div[1]/div[2]/div[2]/div[4]/div/div[2]/input')
                    exception_input.fill(exception)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(1000)

        if b_auto_attach_to_error_pages:
            page.locator('xpath=b_auto_attach_to_error_pages').click()
            page.wait_for_timeout(1000)

    # Proceed with block import
    import_btn = page.locator('.fa-download')
    import_btn.click() # click import button
    page.wait_for_timeout(1000)
    text_field = page.locator('xpath=//*[@id="gjs-mdl-c"]/div/div/div[6]/div[1]/div/div/div/div[5]/div/pre')
    text_field.click() #click the text area
    page.wait_for_timeout(1000)
    text_fill = page.locator('xpath=//*[@id="gjs-mdl-c"]/div/div/div[1]/textarea')
    text_fill.fill(b_html + "\n" + "<style>\n" + b_css + "\n</style>") # fill the text area
    page.wait_for_timeout(2000)
    page.locator('.gjs-btn-import').click() # click import save button
    page.wait_for_timeout(1000)
    page.locator('xpath=//*[@id="wrapper"]/nav/div[2]/div[1]/div[2]/div/div/button[1]').click() # click the save button
    page.wait_for_timeout(2000)
    page.locator('.btn-back-tiered-menu ').click() # click back button
    page.wait_for_timeout(5000)


def search_and_check_block_existence(page, b_title, block_name, instance_id):
    # Locate and interact with the search box
    search_box = page.locator('xpath=//*[@id="search-input"]')
    search_box.click()
    page.keyboard.press("Control+A")
    search_box.fill(b_title)
    search_box.press("Enter")
    page.wait_for_timeout(2000)

    block_exists = False
    matching_elements = page.locator(f"text={b_title}").all()

    if matching_elements:
        rows = page.query_selector_all('table[data-v-4aee22f3][data-v-816643a6] tbody tr')
        for row in rows:
            second_column = row.query_selector("td:nth-child(2)")
            if second_column and second_column.inner_text().strip() == b_title:
                block_exists = True
                print(f"'{b_title}' already exists")

                # Prepare CSV file path
                csv_filename = f"v2_{instance_id}_Duplicate_Blocks.csv"

                # Check if file exists, if not create with header
                file_exists = os.path.isfile(csv_filename)
                with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    if not file_exists:
                        writer.writerow(["b_title", "block_name"])
                    writer.writerow([b_title, block_name])
                break
    return block_exists


def process_blocks(page, sitename, instance_id, blocks_folder):
    page.goto(f"https://{sitename}/builder/website/{instance_id}?panel=left-sidebar-settings--elements")
    page.wait_for_timeout(5000)

    for block_name in os.listdir(blocks_folder):
        if block_name.endswith(".json"):
            block_path = os.path.join(blocks_folder, block_name)
            with open(block_path, "r", encoding="utf-8") as f:
                block_data = json.load(f)
                try:
                    storage = block_data.get("storage", {})
                    if isinstance(storage, dict):
                        data = storage.get("data", {})
                        if isinstance(data, dict) and "css" in data:
                            b_css = data["css"]
                        else:
                            b_css = ""
                    else:
                        b_css = ""
                    b_html = block_data.get("storage", {}).get("data", {}).get("html", "")
                    b_title = block_data.get("settings", {}).get("title", "")
                    settings_settings = block_data.get("settings", {}).get("settings") or {}
                    b_description = settings_settings.get("description", "")
                    b_deleted_by = settings_settings.get("deleted_by", "")
                    b_category = block_data.get("settings", {}).get("category", "")
                    b_protected = block_data.get("settings", {}).get("protected", "")
                    b_files = block_data.get("settings", {}).get("files", [])
                    b_auto_attach = settings_settings.get("auto_attach", False)
                    b_auto_attach_location = settings_settings.get("auto_attach_location", "")
                    b_auto_attach_exceptions = settings_settings.get("auto_attach_exceptions", [])
                    b_auto_attach_to_error_pages = settings_settings.get("auto_attach_to_error_pages", False)

                    if b_deleted_by:
                        print(f"Skipping block '{b_title}' as it was deleted by {b_deleted_by}. Exiting block processing.")
                        # break
                    # block_exists = search_and_check_block_existence(page, b_title, block_name, instance_id)

                    print(f"found block : {b_title} at JSON {block_name}")

                    add_block_button = page.locator('xpath=//*[@id="webbuilder-modal-block-list"]/div/div/div/div[1]/div[2]/a')
                    fresh_site_button = page.locator('xpath=//*[@id="webbuilder-modal-block-list"]/div/div/div/a')

                    if add_block_button.is_visible() and not b_deleted_by:
                        add_block_button.click()
                        print("Clicked Add block list button.")
                        page.wait_for_timeout(1000)
                        create_block(page, b_title, b_description, b_category, b_protected, b_files, b_auto_attach, b_auto_attach_location, b_auto_attach_exceptions, b_auto_attach_to_error_pages, b_html, b_css)
                    elif fresh_site_button.is_visible() and not b_deleted_by:
                        fresh_site_button.click()
                        print("Clicked New site block list button.")
                        page.wait_for_timeout(1000)
                        create_block(page, b_title, b_description, b_category, b_protected, b_files, b_auto_attach, b_auto_attach_location, b_auto_attach_exceptions, b_auto_attach_to_error_pages, b_html, b_css)
                    else:
                        print("Neither block list button was found.")

                except KeyError:
                    print(f"Certain Field Not Found : '{block_name}'")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Load environment variables from .env file
    load_dotenv()

    # Folder containing JSON files
    files_folder = "files"
    pages_folder = "pages"
    blocks_folder = "modules"

    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    sitename = os.getenv('SITENAME')
    instance_id = os.getenv('INSTANCE_ID')

    csv_filename = f"v2_{instance_id}_duplicate_files_list.csv"

    # Create the CSV file once if it doesn't exist
    # CSV File is for noting the Duplicate Files    
    if not os.path.exists(csv_filename):
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Duplicate File Name"])  # Header row


    # Go to dashboard
    page.goto("https://webbuilder.pfizer/webbuilder/dashboard")

    # Click the Webbuilder Login button
    page.click('xpath=//*[@id="app"]/div[1]/div[1]/div[1]/div/div[2]/a')

    # Fill in login credentials
    page.fill('xpath=//*[@id="username"]', username)
    page.fill('xpath=//*[@id="password"]', password)
    page.press('xpath=//*[@id="password"]', "Enter")
    
    # Call the main processing functions in synchronous order
    process_blocks(page, sitename, instance_id, blocks_folder) # completed. released for trials
    
    browser.close()