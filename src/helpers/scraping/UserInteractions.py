from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import json
import time
import os
import uuid

# -------------------------
# Helpers
# -------------------------
def define_session():
    return {"events": []}

def is_product_page(url):
    return "product-details" in url

def save_event(action, file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []

    data.append(action)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    return data


def log_event(session, event_type, link, user_id, duration=None):
    event = {
        "user_id": user_id,
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "product_link": link
    }
    if duration is not None:
        event["duration"] = duration

    session["events"].append(event)

    return session



# -------------------------
# Inject JS trackers
# -------------------------
def inject_buy_tracker(driver):
    driver.execute_script("""
        window.buyClicked = false;
        const attach = () => {
            const btn = document.querySelector("a.common_btn.buy_now");
            if (btn && !btn.dataset.tracked) {
                btn.dataset.tracked = "true";
                btn.addEventListener("click", () => { window.buyClicked = true; });
            }
        };
        attach();
        const obs = new MutationObserver(attach);
        obs.observe(document.body, { childList: true, subtree: true });
    """)

def inject_cart_tracker(driver):
    driver.execute_script("""
        window.cartClicked = false;
        const attach = () => {
            const btn = document.querySelector("a.common_btn[wire\\\\:click\\\\.prevent='addToCart']");
            if (btn && !btn.dataset.tracked) {
                btn.dataset.tracked = "true";
                btn.addEventListener("click", () => { window.cartClicked = true; });
            }
        };
        attach();
        const obs = new MutationObserver(attach);
        obs.observe(document.body, { childList: true, subtree: true });
    """)

# -------------------------
# Main function
# -------------------------
def user_interactions(user_id: str = "user_1", duration_sec: int = 300):
    #file_path = "user_events.json"
    #session_id = str(uuid.uuid4())

    base_dir = os.path.dirname(os.path.abspath(__file__))  # helpers/scraping
    file_path = os.path.join(base_dir, "user_events.json")

    session = define_session()

    # --------------------------
    # Enable GUI on WSL
    # --------------------------
    os.environ["DISPLAY"] = ":0"   # For WSL1
    # For WSL2 you may need:
    # os.environ["DISPLAY"] = os.popen("grep nameserver /etc/resolv.conf | awk '{print $2}'").read().strip() + ":0"

    options = Options()

    # ❌ DO NOT use headless for GUI
    # options.add_argument("--headless=new")

    # Stability flags for WSL
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")

    # Hide automation banner
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Let webdriver-manager handle driver ↔ chrome version
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    # Open main products page
    driver.get("https://afaq-stores.com/products")

    on_product_page = False
    start_time = None
    current_product = None

    # Stop after `duration_sec` seconds
    end_time = time.time() + duration_sec

    try:
        while time.time() < end_time:
            current_url = driver.current_url
            is_product = is_product_page(current_url)

            # ENTER product page
            if is_product and not on_product_page:
                action = log_event(session, "product_open", current_url, user_id=user_id)
                data= save_event(action=action, file_path=file_path)

                start_time = time.time()
                current_product = current_url
                on_product_page = True

                inject_buy_tracker(driver)
                inject_cart_tracker(driver)

            # EXIT product page
            elif not is_product and on_product_page:
                duration = round(time.time() - start_time, 2)
                action = log_event(session, "product_exit", current_product, user_id=user_id, duration=duration)
                data= save_event(action=action, file_path=file_path)

                on_product_page = False
                current_product = None

            # Check buttons inside product page
            if on_product_page:
                buy_clicked = driver.execute_script("return window.buyClicked;")
                cart_clicked = driver.execute_script("return window.cartClicked;")

                if buy_clicked:
                    action = log_event(session, "buy_click", current_product, user_id=user_id)
                    driver.execute_script("window.buyClicked = false;")
                    data= save_event(action=action, file_path=file_path)

                if cart_clicked:
                    action = log_event(session, "add_to_cart", current_product, user_id=user_id)
                    driver.execute_script("window.cartClicked = false;")
                    data= save_event(action=action, file_path=file_path)

            time.sleep(0.1)

    except Exception as e:
        print("Error:", e)
        final_event = []

        final_path = os.path.join(base_dir, "final_interactions.json")
        final_event.append(data[-1])

        with open(final_path, "w") as f:
            json.dump(final_event, f, indent=2)

        driver.quit()
    return final_event


'''
# -------------------------
# Run Example
# -------------------------
if __name__ == "__main__":
    user_interactions(user_id="user_2", duration_sec=300)  # 5 min tracking
'''