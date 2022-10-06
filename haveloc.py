from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import csv, os, json
from datetime import datetime

from rich.console import Console
# from rich.columns import Columns
from rich.table import Table
# from rich.panel import Panel

options =  webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('log-level=3')

flag = False
if os.path.exists('credentials.json'):
    try:
        with open('credentials.json', 'r') as f:
            values = json.loads(f.read())
            if len(values) == 0:
                flag = True
            elif 'Username' not in values.keys() or 'Password' not in values.keys():
                flag = True
    except json.JSONDecodeError:
        flag = True
else:
    flag = True

if flag:
    uname = input("Enter your haveloc username: ")
    passw = input("Enter your haveloc password: ")
    values = {}
    values['Username'] = uname
    values['Password'] = passw
    with open('credentials.json', 'w') as f:
        json.dump(values, f)

url = "https://app.haveloc.com/login"

driver = webdriver.Chrome("chromedriver", options = options)
driver.set_window_size(1920, 1080)

driver.get(url)

loginBox = driver.find_element("xpath", '//*[@id="root"]/div/div/form/div[1]/input')
loginBox.send_keys(values['Username'])

passBox = driver.find_element("xpath", '//*[@id="root"]/div/div/form/div[2]/input')
passBox.send_keys(values['Password'])

sleep(2)

source = driver.find_element("xpath",'//*[@id="root"]/div/div/form/div[3]/span')
action = webdriver.ActionChains(driver)
action.move_to_element(source).perform()

sleep(2)

xOffset = 0
yOffset = 100
webdriver.ActionChains(driver).move_by_offset(xOffset,yOffset).click().perform()

nextButton = driver.find_element("xpath", '//*[@id="root"]/div/div/form/button')
sleep(2)
nextButton.click()

# import pdb; pdb.set_trace()  
sleep(3)  

page_source = driver.page_source

soup = BeautifulSoup(page_source,features="html5lib")
PAGE_SIZE = int(''.join(filter(str.isdigit, soup.find_all("div", {"class": "bottomNavButtons"})[0].contents[1].contents[1].contents[0]))) + 1

fresherJobsurl = '''https://app.haveloc.com/FresherJobs?{"magicBoard":{
                                "pageSizeObj":'''+str(PAGE_SIZE)+''',
                                "filterObj":[],
                                "sortObj":[
                                    {
                                        "key":"jobApplyBy",
                                        "operation":"desc"
                                    }
                                ]
                            }
                        }
'''

driver.get(fresherJobsurl)

sleep(5)

page_source = driver.page_source

soup = BeautifulSoup(page_source,features="html5lib")

mydivs = soup.find_all("div", {"class": "mainCard"})
allCompanies = []
for i in mydivs:
    jobTitle = i.find("a",{"class": "cont1LeftTitle"}).contents[0]
    companyName = i.find("div", {"class": "cont1RightTitle"}).contents[0]
    companyLocation = i.find("div", {"class": "cont1LeftCollege"}).contents[0].strip()
    companyCTC = i.find_all("div", {"class": "singleTopicDesc"})[0].contents[0]

    applyBy = i.find_all("div", {"class": "singleTopicDesc"})[1].contents[0]
    month_map = {
        'jan': '01',
        'feb': '02',
        'mar': '03',
        'apr': '04',
        'may': '05',
        'jun': '06',
        'jul': '07',
        'aug': '08',
        'sep': '09',
        'oct': '10',
        'nov': '11',
        'dec': '12',
    }
    date1, time = [j.strip() for j in applyBy.split('by')]
    date1 = date1.split()
    date1 = date1[0]+'-'+month_map[date1[1].lower()]+'-'+date1[2]

    jobStat = i.find_all("div", {"class": "jbStatTitle"})[0].contents
    jobCat = jobStat[0].contents[0].replace(',','').replace('#','').strip()
    jobStat = jobStat[1].strip()

    applicants = i.find_all("span", {"class": "hiredVsApp"})[0].contents[0].replace('Applicants','').strip()

    hrefs = i.find_all('a', href=True)
    jobApply = hrefs[0]['href']
    compDetails = hrefs[1]['href']
    
    allCompanies.append(
        {
            'Company Name': companyName,
            'Job Title': jobTitle,
            'CTC': companyCTC,
            'Apply By date': date1,
            "Apply By time": time,
            "Company Location": companyLocation,
            "Job Category": jobCat,
            "Job status": jobStat,
            "Number of applicants": applicants,
            "jobApply": jobApply,
            "compDetails": compDetails
        }
    )


fieldnames = ['Company Name', 'Job Title', 'CTC', 'Apply By date', 'Apply By time', 'Company Location', 'Job Category', 'Job status', 'Number of applicants']

os.system('cls')
checc = input("Do you want to export the companies data? (Y/N): ")

temp = []
if checc.lower() == "y":
    for x in allCompanies:
        temp.append({key: x[key] for key in x if key not in ['jobApply', 'compDetails']})

    with open(os.path.expanduser("~/Desktop")+'/companies.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(temp)
    
baseUrl = 'https://app.haveloc.com'

datetimern = datetime.now()

old = driver.window_handles
driver.execute_script("window.open('');")
new = driver.window_handles

os.system('cls')
print('Saved as companies.csv on desktop')
sleep(3)

combine = list(set(new) & set(old))
new_tab = list(set(new) - set(old))[0]

for tab in combine:
    driver.switch_to.window(tab)
    driver.close()

driver.switch_to.window(new_tab)

table = Table(show_header=True, header_style="bold cyan")
table.add_column("Company Name")
table.add_column("Job Title")
table.add_column("CTC")
table.add_column("Date deadline")
table.add_column("Time deadline")

appliable_companies = []
for i in allCompanies:
    datetime_str = ''.join([x for x in i['Apply By date']])+":"+time.replace(":","-")
    datetime_object = datetime.strptime(datetime_str, '%d-%m-%Y:%H-%M') # create date and time object with the apply by time and date
    if datetime_object > datetimern:
        appliable_companies.append(i)
    else:
        break

for i in appliable_companies:
    table.add_row(
                i['Company Name'], i["Job Title"], i["CTC"], i["Apply By date"], i["Apply By time"]
                )
    table.add_row()
    
Console().print(table)

chek = input("Do you want to apply to these companies? (Y/N)")

if chek.lower() == "y":
    for i in appliable_companies:
        datetime_str = ''.join([x for x in i['Apply By date']])+":"+time.replace(":","-")
        datetime_object = datetime.strptime(datetime_str, '%d-%m-%Y:%H-%M') # create date and time object with the apply by time and date
        if datetime_object > datetimern:
            print("\n=================================================================\n")
            print(f"Company Name: \t{i['Company Name']}")
            print(f"Job Title: \t{i['Job Title']}")
            print(f"CTC: \t\t{i['CTC']}")
            print(f"Deadline date: \t{i['Apply By date']}")
            print(f"Deadline time: \t{i['Apply By time']}\n")
            
            check = input("\nDo you want to apply to this company? (Y/N): ")

            os.system('cls')
            Console().print(table)

            
            if check.lower() == "y":
                
                driver.window_handles[0]
                driver.get(baseUrl+i['jobApply'])

                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])

                driver.get(baseUrl+i['compDetails'])
                input('Press Enter to continue to the next job application')
                
                old = driver.window_handles
                driver.execute_script("window.open('');")
                new = driver.window_handles
                
                combine = list(set(new) & set(old))
                new_tab = list(set(new) - set(old))[0]
                
                for tab in combine:
                    driver.switch_to.window(tab)
                    driver.close()
                
                driver.switch_to.window(new_tab)
                
                print("\n=================================================================\n")
                
                os.system('cls')
                Console().print(table)
