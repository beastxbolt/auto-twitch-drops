from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
import time
import datetime
from config import discord_webhook_url, twitch_client_id, twitch_client_secret

streamer_1 = "Rocketleague"
streamer_2 = "CollegeCarBall"

streamer_name = streamer_1
user_id = 456055164886056961
start_time = datetime.datetime.utcnow()

cap = DesiredCapabilities().CHROME
cap["marionette"] = False

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-data-dir=C:/Users/Administrator/AppData/Local/Google/Chrome/User Data")


def send_message(message):
    payload = {'content': message}
    headers = {'Content-Type': 'application/json'}
    requests.post(discord_webhook_url, json=payload, headers=headers)
    return


def checkStream():
    global streamer_name
    time.sleep(3)
    send_message(
        f"Checking If {streamer_name} Is Live On Twitch\nLog Timestamp - `{datetime.datetime.now()}`")
    body = {
        'client_id': twitch_client_id,
        'client_secret': twitch_client_secret,
        "grant_type": 'client_credentials'
    }

    r = requests.post('https://id.twitch.tv/oauth2/token', body)
    keys = r.json()

    headers = {
        'Client-ID': twitch_client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }

    stream = requests.get(
        'https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)

    stream_data = stream.json()
    time.sleep(3)
    if len(stream_data['data']) == 1:
        if stream_data['data'][0]['type'] == "live":
            send_message(
                f"**{streamer_name}** Is Live\nLog Timestamp - `{datetime.datetime.now()}`")
            time.sleep(3)
            return True
    else:
        send_message(
            f"**{streamer_name}** Has NOT Started Stream Or Has Gone Offline\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(3)
        if streamer_name == streamer_1:
            streamer_name = streamer_2
        elif streamer_name == streamer_2:
            streamer_name = streamer_1
        send_message(
            f"Switched Streamer Name To - **{streamer_name}**\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(3)
        return False


def watchStream():
    global streamer_name
    driver = webdriver.Chrome(desired_capabilities=cap, options=options)
    driver.get(f"https://www.twitch.tv/{streamer_name}")
    time.sleep(3)
    send_message(
        f"Watching **{streamer_name}** Live Stream Now\nLog Timestamp - `{datetime.datetime.now()}`")
    time.sleep(1800)
    while True:
        if checkStream() is True:
            send_message(
                f"Continuing To Watch **{streamer_name}** Livestream\nLog Timestamp - `{datetime.datetime.now()}`")
            claimDrop(driver)
            time.sleep(1800)
        else:
            if streamer_name == streamer_1:
                streamer_name = streamer_2
            elif streamer_name == streamer_2:
                streamer_name = streamer_1
            send_message(
                f"**{streamer_name}** Went Offline. Checking For Drops\nLog Timestamp - `{datetime.datetime.now()}`")
            claimDrop(driver)
            time.sleep(1)
            driver.quit()
            send_message(
                f"**{streamer_name}** Is Offline. Stopped Watching Livestream\nLog Timestamp - `{datetime.datetime.now()}`")
            time.sleep(3)
            if streamer_name == streamer_1:
                streamer_name = streamer_2
            elif streamer_name == streamer_2:
                streamer_name = streamer_1
            send_message(
                f"Switched Streamer Name To - **{streamer_name}**\nLog Timestamp - `{datetime.datetime.now()}`")
            break


def claimDrop(driver):
    try:
        driver.execute_script(
            "inventoryWindow = window.open('https://twitch.tv/drops/inventory','_blank')")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        send_message(
            f"Opening Inventory To Check Drops\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(3)
        claimButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Claim Now')]")))
        claimButton.click()
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[0])
        send_message(
            f"**Drop Claimed Successfully**\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(3)
        driver.execute_script("inventoryWindow.close()")
        send_message(
            f"**Inventory Window Closed**\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(2)
        return
    except:
        driver.switch_to.window(driver.window_handles[0])
        send_message(
            f"**Drop Cannot Be Claimed Right Now**\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(3)
        driver.execute_script("inventoryWindow.close()")
        send_message(
            f"Inventory Window Closed\nLog Timestamp - `{datetime.datetime.now()}`")
        time.sleep(2)
        return


def main():
    while True:
        if checkStream() is True:
            watchStream()
        else:
            if checkStream() is True:
                watchStream()
            else:
                send_message(
                    f"Both Streamers Are Offline. Checking Again After 30 Min\nLog Timestamp - `{datetime.datetime.now()}`")
                time.sleep(1800)
                continue


if __name__ == "__main__":
    print("Running Script...")
    time.sleep(3)
    main()
