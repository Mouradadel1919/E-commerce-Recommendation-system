from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

# -------------------------
# Chrome options for WSL/Linux
# -------------------------
options = Options()
options.binary_location = "/usr/bin/google-chrome"  # <-- Chrome binary path
options.add_argument("--no-sandbox")               # WSL fix
options.add_argument("--disable-dev-shm-usage")    # WSL memory fix
#options.add_argument("--headless=new")             # Headless mode
options.add_argument("--disable-gpu")              # Optional
options.add_argument("--window-size=1920,1080")    # Optional
options.add_argument("--start-maximized")          # Optional

# -------------------------
# Chromedriver setup using webdriver_manager
# -------------------------
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)

# -------------------------
# WebDriverWait
# -------------------------
wait = WebDriverWait(driver, 15)

# -------------------------
# Test
# -------------------------
driver.get("https://www.google.com")
print("Page title:", driver.title)

# -------------------------
# Clean up
# -------------------------
input("Press Enter to close browser...")
driver.quit()
