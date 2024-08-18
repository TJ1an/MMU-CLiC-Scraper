from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv

schedule_data = []
all_subjects = []

load_dotenv()

USERID = os.getenv('USERID')
PASSWORD = os.getenv('PASSWORD')

def convert_to_iso(schedule, date_range):

    time_range = schedule.split(' ', 1)
    start_time_str, end_time_str = time_range[1].split(' - ')

    start_date_str, end_date_str = date_range.split(' - ')
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')

    start_time = datetime.strptime(start_time_str, '%I:%M%p').time()
    end_time = datetime.strptime(end_time_str, '%I:%M%p').time()

    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(start_date, end_time)

    iso_start = start_datetime.isoformat()
    iso_end = end_datetime.isoformat()

    return {
        "startDateTime": f"{iso_start}+08:00",
        "endDateTime": f"{iso_end}+08:00"
    }


def scrape():
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.get("https://clic.mmu.edu.my/psp/csprd/?&cmd=login&languageCd=ENG")

    # Find and fill the login form
    driver.find_element(By.NAME, 'userid').send_keys(USERID)
    driver.find_element(By.NAME, 'pwd').send_keys(PASSWORD)

    # Submit the form
    driver.find_element(By.NAME, 'Submit').click()

    # Navigate to the schedule page
    driver.get('https://clic.mmu.edu.my/psp/csprd/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL?PORTALPARAM_PTCNAV=HC_SSR_SSENRL_LIST&EOPP.SCNode=SA&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=CO_EMPLOYEE_SELF_SERVICE&EOPP.SCLabel=Course%20Enrollment&EOPP.SCFName=N_NEW_CRSENRL&EOPP.SCSecondary=true&EOPP.SCPTfname=N_NEW_CRSENRL&FolderPath=PORTAL_ROOT_OBJECT.CO_EMPLOYEE_SELF_SERVICE.N_NEW_ACADEMICS.N_NEW_CRSENRL.N_NEW_CLASSSCH.HC_SSR_SSENRL_LIST&IsFolder=false')
    wait = WebDriverWait(driver, 10)
    frame = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id='ptifrmtgtframe']")))
    driver.switch_to.frame(frame)
    page_source = driver.page_source


    driver.close()

    soup = BeautifulSoup(page_source, 'html.parser')
    subjects = soup.find_all('td', class_='PAGROUPDIVIDER PSLEFTCORNER')
    tables = soup.find_all('table', {"id": lambda L: L and L.startswith('CLASS_MTG_VW$scroll$')})
    print(" ")
    print("Subjects this semester: ")
    print(" ")
    for subject in subjects:
        all_subjects.append(subject.text)
        print(subject.text)
    print(" ")
        

    subject_index = 0

    for table in tables:
        rows = table.find_all('tbody')
        for row in rows:
            cells = row.find_all('span')
            if cells:
                # Extract cell data
                section = cells[1].get_text(strip=True)
                component = cells[2].get_text(strip=True)
                sched = cells[3].get_text(strip=True)
                room = cells[4].get_text(strip=True)
                dates = cells[5].get_text(strip=True)
                iso_times = convert_to_iso(sched, dates)
                event = {
                    "subject": all_subjects[subject_index] + " | " + section + " | " + component,
                    "start": iso_times['startDateTime'],
                    "end": iso_times['endDateTime'],
                    "room": room,
                    "dates": dates
                }
        schedule_data.append(event)             
        for i in range(6, len(cells)):
            cell_value = cells[i].get_text(strip=True)
            if cell_value == "":
                sched = cells[8].get_text(strip=True)
                dates = cells[10].get_text(strip=True)
                iso_times = convert_to_iso(sched, dates)
                event2 = {
                    "subject": all_subjects[subject_index] + " | " + section + " | " + component,
                    "start": iso_times['startDateTime'],
                    "end": iso_times['endDateTime'],
                    "room": cells[9].get_text(strip=True),
                    "dates": cells[10].get_text(strip=True)
                }
            elif cell_value == None:
                break
            else:
                section2 = cells[6].get_text(strip=True)
                component2 = cells[7].get_text(strip=True)
                sched2 = cells[8].get_text(strip=True)
                iso_times2 = convert_to_iso(sched2, dates)
                event2 = {
                    "subject": all_subjects[subject_index] + " | " + section2 + " | " + component2,
                    "start": iso_times2['startDateTime'],
                    "end": iso_times2['endDateTime'],
                    "room": cells[9].get_text(strip=True),
                    "dates": cells[10].get_text(strip=True)
                }
            schedule_data.append(event2)
            break
        subject_index += 1

    return schedule_data

# def main():
#     data = scrape()
#     for event in data:
#         print(event)

# if __name__ == "__main__":
#     main()
