import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()
password = os.getenv("password_mail")
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)


driver = webdriver.Chrome(options=options)



def close_popup():
    try:
        popup_close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))
        )
        popup_close_button.click()
        print("Popup closed")
    except Exception as e:
        print(f"No popup to close: {e}")


def google_search(query):
    driver.get("https://fr.indeed.com/")
    close_popup()
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "q"))
        )
        print("Search box found")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)

        date_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "dateLabel"))
        )
        date_filter.click()
    except Exception as e:
        print(f"Error during search: {e}")
        driver.quit()


def send_email(subject, body, to_email, mdp):
    from_email = "dipitay@gmail.com"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, mdp)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


query = "Ingénieur QA"
google_search(query)

df = pd.DataFrame({'Link': [], 'Job Title': [], 'Company': [], 'Date Posted': [], 'Location': []})

while True:
    soup = BeautifulSoup(driver.page_source, 'lxml')
    boxes = soup.find_all('div', class_='job_seen_beacon')

    for i in boxes:
        link = i.find('a').get('href')
        job_title = i.find('a', class_ = 'jcs-JobTitle css-jspxzf eu4oa1w0')
        company = i.find('span', class_='company-name')
        location = i.find('div', class_='css-1p0sjhy eu4oa1w0')
        date_posted = i.find('span', class_='css-10pe3me eu4oa1w0')
        df = df._append({'Link': link, 'Job Title': job_title, 'Company': company, 'Date Posted': date_posted,
                        'Location': location}, ignore_index=True)
        print(df)

    # Move to the next page
    try:
        next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
        next_button.click()
        time.sleep(2)
    except:
        break

# Format email body
email_body = "Here are the latest job postings:\n\n"
for index, row in df.iterrows():
    email_body += f"Link: https://fr.indeed.com{row['Link']}\n\n"

# Send email
send_email("Latest Job Postings", email_body, "dipitay@gmail.com", password)


