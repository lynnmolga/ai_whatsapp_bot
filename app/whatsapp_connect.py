import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

driver = None

def create_driver():
    options = Options()
    options.add_argument("--window-size=1200,900")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

def open_whatsapp():
    global driver
    if driver is None:
        driver = create_driver()
    driver.get("https://web.whatsapp.com")
    print("Scan QR code if needed")
    time.sleep(25)


def find_chat(chat_name, max_wait=20):
    target = chat_name.strip().lower()
    start = time.time()
    while time.time() - start < max_wait:
        chats = driver.find_elements(By.XPATH, '//span[@title]')
        for chat in chats:
            title = chat.get_attribute("title")
            if not title:
                continue
            normalized = title.strip().lower()
            if target in normalized:
                print(f"Found chat: {title}")
                return chat
        time.sleep(1)
    print(f"Chat not found after {max_wait}s: {chat_name}")
    return None


def get_last_message(chat_name):
    try:
        chat = find_chat(chat_name)
        if not chat:
            print(f"Chat not found: {chat_name}")
            return None
        chat.click()
        time.sleep(2)
        incoming_bubbles = driver.find_elements(
            By.XPATH,
            '//div[contains(@class,"message-in")]'
        )
        if not incoming_bubbles:
            print("No incoming message bubbles found")
            return None
        raw_text = incoming_bubbles[-1].text.strip()
        if not raw_text:
            print("Incoming bubble found, but text is empty")
            return None
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        lines = [
            line for line in lines
            if not re.match(r"^\d{1,2}:\d{2}$", line)
        ]
        lines = [
        line for line in lines
        if not re.match(r"^\d{1,2}:\d{2}(\s?[AP]M)?$", line, re.IGNORECASE)
        ]
        if not lines:
            return None
        return "\n".join(lines)
    except Exception as e:
        print("Get message error:", e)
        return None


def send_message(text):
    try:
        boxes = driver.find_elements(
            By.XPATH,
            '//div[@contenteditable="true"]'
        )
        box = boxes[-1]
        box.click()
        box.send_keys(text)
        box.send_keys(Keys.ENTER)
    except Exception as e:
        print("Send error:", e)