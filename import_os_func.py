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
    page.wait_for_timeout(2000)


def search_and_check_block_existence(page, b_title):
    search_box = page.locator('xpath=//*[@id="search-input"]')
    search_box.click()
    page.keyboard.press("Control+A")
    search_box.fill(b_title)
    search_box.press("Enter")
    page.wait_for_timeout(2000)

    block_exists = False
    if page.locator(f"text={b_title}").is_visible():
        rows = page.query_selector_all('table[data-v-4aee22f3][data-v-816643a6] tbody tr')
        for i, row in enumerate(rows):
            second_column = row.query_selector("td:nth-child(2)")
            if second_column.inner_text().strip() == b_title:
                block_exists = True
                print(f"'{b_title} already exists")
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
                    b_css = block_data.get("storage", {}).get("data", {}).get("css", "")
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
                    
                    block_exists = search_and_check_block_existence(page, b_title)

                    print(f"found block : {block_name}")

                    add_block_button = page.locator('xpath=//*[@id="webbuilder-modal-block-list"]/div/div/div/div[1]/div[2]/a')
                    fresh_site_button = page.locator('xpath=//*[@id="webbuilder-modal-block-list"]/div/div/div/a')

                    if add_block_button.is_visible() and not block_exists and not b_deleted_by:
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


def process_files(page, sitename, instance_id, files_folder, pages_folder):
    # Navigate to Content > Files
    page.goto(f"https://{sitename}/builder/website/{instance_id}?panel=left-sidebar-settings--file-manager")
    page.wait_for_timeout(5000)

    skipped_file_csv = f"v2_{instance_id}_skipped.csv"

    # Step 4: Scan all JSON files in the folder
    for file_name in os.listdir(files_folder):
        f_name = ""
        f_path = ""
        f_url = ""
        f_category = ""
        f_only_on_deploy = ""
        f_deploy_on = ""
        f_weight = ""
        f_pages = []
        f_private = ""
        f_footer = ""
        f_header = ""
        f_async = ""
        f_modular = ""

        print(len(os.listdir(files_folder)))

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
                f_private = data["details"]["private"]
                f_footer = data["details"]["footer_file"]
                f_header = data["details"]["header_file"]
                f_async = data["details"]["async"]
                f_modular = data["details"]["modular"]

                # Convert the Variables to String
                f_path_str = str(f_path)
                f_url_str = str(f_url)
                f_only_on_deploy_str = str(f_only_on_deploy)
                f_deploy_on_str = str(f_deploy_on)
                f_category_str = str(f_category)
                f_weight_str = str(f_weight)
                f_private_str = str(f_private)
                f_footer_str = str(f_footer)
                f_header_str = str(f_header)

                for key, value in f_pages.items():
                    print(f"File is : '{f_name}' for JSON file '{file_name}'")
                # pages_count = len(f_pages)
                # print(pages_count)

            # Search for file name
            search_box = page.locator('xpath=//*[@id="file-search-text-input"]')
            search_box.click()
            page.keyboard.press("Control+A")
            search_box.fill(f_name)
            search_box.press("Enter")
            page.wait_for_timeout(3000)

            # Check if file name appears in page
            file_visible = page.locator(f"text={f_name}")
            file_visible_count = file_visible.count()

            if file_visible_count > 1:
                print(f"Duplicate File Name : '{f_name}' is DUPLICATE hence SKIPPING !!")

                with open(csv_filename, mode='a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([f_name])

            else:
                if page.locator(f"text={f_name}").is_visible():
                    rows = page.query_selector_all('table[data-v-7a2af82c] tbody tr')

                    # Scan each row for the exact value from Table
                    for i, row in enumerate(rows):
                        first_column = row.query_selector("td:nth-child(1)")
                        if first_column.inner_text().strip() == f_name:
                            index = i + 1
                    
                    print(f"File Name '{f_name}' FOUND !!!! at Index {index}")
                    
                    # Click edit icon of File
                    page.locator(f'xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div/div[2]/table/tbody/tr[{index}]/td[7]/div/span[1]/a/i').click()
                    page.wait_for_timeout(2000)

                    # Paste the pages data in the file config
                    for key, value in f_pages.items():
                        pages_count = len(f_pages)
                        if pages_count <= 1:
                            # attach_page = page.locator('xpath=//*[@id="attachToAll"]')
                            if page.locator('xpath=//*[@id="attachToAll"]').is_visible():
                                page.locator('xpath=//*[@id="attachToAll"]').click()
                                page.wait_for_timeout(1000)
                        else:
                            for page_path in os.listdir(pages_folder):
                                # print(index)
                                if page_path.endswith(".json"):
                                    page_file_path = os.path.join(pages_folder, page_path)
                                    with open(page_file_path, "r", encoding="utf-8") as f:
                                        page_data = json.load(f)
                                        p_title = page_data['settings']['title']
                                        p_uuid = page_data['settings']['uuid']

                                    if key == p_uuid and page.locator('xpath=//*[@id="attachToIndividual"]').is_visible():
                                        page.locator('xpath=//*[@id="attachToIndividual"]').click() #click on Individial Pages Radio Button
                                        if pages_count == 2:
                                            # Locate all <li> elements inside the specified <ul>
                                            li_locator = page.locator('xpath=/html/body/div[1]/div[1]/div[7]/div/div/div[2]/div/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[3]/ul/li/span')
                                            span_texts = li_locator.all_text_contents()

                                            # print("Available span texts in listbox:")
                                            # for text in span_texts:
                                            #     print(f"- {text}")

                                            if p_title in span_texts:
                                                page.locator('xpath=//*[@id="attachToIndividual"]').click()  # Click on Individual Pages Radio Button
                                                page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]').click()
                                                add_individual_pages = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]/input')
                                                add_individual_pages.fill(p_title)
                                                page.keyboard.press("Enter")
                                                page.wait_for_timeout(700)
                                            else:
                                                page.locator('xpath=//*[@id="attachToAll"]').click()
                                                page.wait_for_timeout(1000)

                                        elif pages_count > 2:
                                            page.locator('xpath=//*[@id="attachToIndividual"]').click()  # Click on Individual Pages Radio Button
                                            page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]').click()
                                            add_individual_pages = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[2]/div[3]/div/div[2]/input')
                                            add_individual_pages.fill(p_title)
                                            page.keyboard.press("Enter")
                                            page.wait_for_timeout(700)
                    # Paste file details in field
                    if f_private != False:
                        private_field = page.locator('xpath=//*[@id="privateFile"]').visible()
                        if private_field.visible():
                            private_field.click()
                            page.wait_for_timeout(1000)

                    # Only proceed if header or footer is set and the section is visible
                    if (f_header_str != "0" or f_footer_str != "0") and page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[3]').is_visible():
                        # Scope to the specific div containing the radio buttons
                        placement_section = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[2]/div[3]')
                        # Determine which value to select
                        if f_header_str != "0":
                            placement_value = "header"
                        elif f_footer_str != "0":
                            placement_value = "footer"
                        else:
                            placement_value = "none"
                        # Select the correct radio button within the scoped section
                        placement_radio = placement_section.locator(f'input[type="radio"][value="{placement_value}"]')
                        placement_radio.click(force=True)
                        page.wait_for_timeout(1000)

                    if f_async != False:
                        async_field = page.locator('xpath=//*[@id="cssLoadingAsync"]') # for css file
                        if async_field.is_visible():
                            async_field.click()
                            page.wait_for_timeout(1000)
                        elif page.locator('xpath=//*[@id="fileloadasAsync"]').is_visible():
                            page.locator('xpath=//*[@id="fileloadasAsync"]').click() # for js or any other files
                            page.wait_for_timeout(1000)
                    elif page.locator('xpath=//*[@id="fileloadasDefer"]').is_visible():
                        page.locator('xpath=//*[@id="fileloadasDefer"]').click()
                        page.locator('xpath=//*[@id="fileloadasDefer"]')
                        page.wait_for_timeout(1000)
                    else:
                        page.wait_for_timeout(1000)

                    weight_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[2]/input')
                    if weight_field.is_visible():
                        weight_field.click()
                        page.keyboard.press("Control+A")
                        weight_field.fill(f_weight_str)
                        page.wait_for_timeout(1000)
                    
                    if f_modular != False:
                        modular_field = page.locator('xpath=//*[@id="modularFile"]')
                        modular_field.click()
                        page.wait_for_timeout(1000)

                    path_field = page.locator("input[name='filepath']")
                    if f_path_str and f_path_str != "None":
                        path_field.click()
                        page.keyboard.press("Control+A")
                        path_field.fill(f_path_str)
                        page.wait_for_timeout(1000)

                    category_span = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[3]/div/div[2]/span')
                    if category_span.is_visible():
                        span_text = category_span.inner_text().strip()
                        # Check if f_category_str has a value (not empty and not None)
                        if f_category_str and f_category_str.strip() and f_category_str != span_text and f_category_str.strip() != "None":
                            category_field = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[3]/div/div[2]/span')
                            category_field.click()
                            page.wait_for_timeout(1000)
                            category_fill = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[2]/div[3]/div[3]/div/div[2]/input')
                            category_fill.fill(f_category_str)
                            page.wait_for_timeout(2000)
                            page.keyboard.press("Enter")
                            page.wait_for_timeout(1000)

                    # Step 9: Click Save button
                    save_button = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[1]/div[2]/div[2]/button')
                    cancel_button = page.locator('xpath=//*[@id="webbuilder-editor-content-wrapper"]/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div/form/div[1]/div[2]/div[1]/button')

                    if save_button.get_attribute("disabled") is not None:
                        # Click the cancel button
                        cancel_button.click()
                        page.wait_for_timeout(1000)

                        # Create the CSV file only once if it doesn't exist
                        if not os.path.exists(skipped_file_csv):
                            with open(skipped_file_csv, mode='w', newline='', encoding='utf-8') as file:
                                writer = csv.writer(file)
                                writer.writerow(["Skipped File Name"])

                        # Append the skipped file name to the CSV
                        with open(skipped_file_csv, mode='a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow([f_name])
                    else:
                        # Click the save button
                        save_button.click()
                        page.wait_for_timeout(1000)

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
    # process_files(page, sitename, instance_id, files_folder, pages_folder) # completed. released for trials
    
    browser.close()