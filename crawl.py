
import time
import pandas as pd
from helium import start_chrome
from bs4 import BeautifulSoup
import requests
import math
import logging
import random


# 芬兰
# keywords = 'Data Scientist' # 'Python (Programming Language)' # search keyword
# location = 'Finland' # search location
# geoId = '100456013' # '100293800' # search location id 
# currentJobId = '3415227738' # current job id
# 爱尔兰
keywords = 'Data Scientist' # 'Python (Programming Language)' # search keyword
location = 'Ireland' # search location
geoId = '104738515' # '100293800' # search location id 
currentJobId = '3415227738' # current job id

fout = open('linkedinjobs.txt', 'w', encoding='utf-8')

def process_detail(jobid):
    detail_url = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'.format(jobid) # debug: https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/3641771427
    print(detail_url)
    try:
        # browser = start_chrome(detail_url, headless=True)
        # soup = BeautifulSoup(browser.page_source, 'html.parser')
        resp = requests.get(detail_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
    except:
        print('job detail页面打开失败，休眠1~5秒后重试，jobid=', jobid)
        time.sleep(random.randint(1, 5))
        return process_detail(jobid) # TODO 再次调用自身，可能陷入无限循环

    info = {}
    try:
        info["company"] = soup.find("div",{"class":"top-card-layout__card"}).find("a").find("img").get('alt')    
    except:
        info["company"] = ''
    try:
        info["job-title"] = soup.find("div",{"class":"top-card-layout__entity-info"}).find("a").text.strip()
    except:
        info["job-title"] = ''
    try:
        info["level"] = soup.find("ul",{"class":"description__job-criteria-list"}).find("li").text.replace("Seniority level","").strip()
    except:
        info["level"] = ''
    try:
        info["job description"] = soup.find("div",{"class":"show-more-less-html__markup"}).text.strip()
    except:
        info["job description"] = ''
    try:
        info['post-time'] = soup.find("span", {"class": "posted-time-ago__text"}).text.strip()
    except:
        info['post-time'] = ''
    try:
        info['employment-type'] = soup.find_all("li",{"class":"description__job-criteria-item"})[1].text.replace("Employment type","").strip()
    except:
        info['employment-type'] = ''
    info['link'] = '=HYPERLINK("{}","点击链接")'.format(detail_url)
    info['jobid'] = jobid
    info['country'] = location
    info['keywords'] = keywords
    info['geoId'] = geoId
    info['currentJobId'] = currentJobId # 不知道干啥的

    time.sleep(random.randint(1,3))

    fout.write(str(info)+'\n')
    return info


jobid_f = open('{}_jobid.txt'.format(location), 'w+')
jobid_lst = []
result = []
count = 0
page_num = 0
# https://www.linkedin.com/jobs/search?keywords=Data%20Scientist&location=Finland&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0
while True:
    target_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&geoId={}&currentJobId={}&start={}'.format(keywords, location, geoId, currentJobId, page_num)
    print('====', target_url, '====')
    try:
        browser = start_chrome(target_url, headless=True)
    except:
        print('job list页面打开失败，休眠1~3秒后重试，page_num=', page_num)
        time.sleep(random.randint(1, 3))
        continue
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    alljobs_on_this_page = soup.find_all("li")
    # 若当前页面不可访问
    if len(alljobs_on_this_page) == 0: break # 结束循环
    for j in range(0, len(alljobs_on_this_page)):
        try:
            jobid = alljobs_on_this_page[j].find("div",{"class":"base-card"}).get('data-entity-urn').split(":")[3]
            jobid_lst.append(jobid)
            jobid_f.write("%s\n" % jobid)
        except:
            print('jobid解析失败')
    page_num += 1 # 页数
    if page_num == 30: 
        break

jobid_f.close()


print("当前jobid数：",len(jobid_lst))
for i, jobid in enumerate(jobid_lst):
    print(i)
    detail = process_detail(jobid)
    if not detail or len(detail) > 0:
        result.append(detail)
        # time.sleep(random.randint(1, 3)) # 没用
    

df = pd.DataFrame(result)
df.to_excel('linkedinjobs.xlsx')