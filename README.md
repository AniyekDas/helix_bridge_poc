
# helix_bridge_poc

Automated script using Playwright to interact with a web dashboard and upload JSON-based content. This project is designed to streamline content management tasks via browser automation.

## 📦 Clone the Repository

```bash
git clone https://github.com/AniyekDas/helix_bridge_poc
cd helix_bridge_poc
```

## Add the folders of Files, Pages, Modules, Settings Folder Downloaded from V1 Site through Export Functionalty, in the above repository folder in local.
# Every File inside each category folder should be in the json format.
 

## 🐍 Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scriptsctivate`
```

## 📚 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔐 Set Up Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open `.env` and fill in the required values:

```env
USERNAME=your_username_here
PASSWORD=your_password_here
SITENAME=your_site_here.com //not needed as it wil be a default value
INSTANCE_ID=your_instance_id_here
```

> These variables are used by `import_data_v2.py` to log in and interact with the dashboard.

## 🚀 Run the Main Script

Make sure you have the required folders (`files/` and `pages/`) populated with valid JSON files.

```bash
python import_data_v2.py
```

This script will:
- Log into the dashboard using Playwright.
- Navigate to the file manager.
- Upload and configure JSON files based on their metadata.
- Attach them to pages as specified.

## 🧰 Requirements

The project uses a wide range of packages including:
- `playwright`
- `python-dotenv`
- `beautifulsoup4`
- `Django`
- `pandas`
- `selenium`
- `chromadb`
- and many more...

Refer to `requirements.txt` for the full list.
