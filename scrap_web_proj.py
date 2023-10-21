import  requests
from bs4 import BeautifulSoup as bs
import numpy as np
import re
import pandas as pd

def get_job_url(main_url):
    #########Phase1: Get the link to all of the pages##############
    r1 = requests.get(main_url)
    soup1 = bs(r1.content,  features="html.parser")
    # # print(soup1.prettify())
    #
    # page_no = soup1.select("._16b9myk0._3reozq0._3reozq1.y44q7i0.y44q7i1.y44q7i21.y44q7ii.y44q7i26.y44q7i18._1hbhsw632")

    #To get the total number of pages
    url = "https://www.jobstreet.com.sg"
    total_pages = int(soup1.select("#pagination option")[-1]['value'])  #####3REFER TO NO1####
    print(total_pages)

    #To  get the link of all the different pages
    link = soup1.select(".z1s6m00._1hbhsw6ce._1hbhsw6p a")[0].get("href")       ##REFER TO NO2####
    # total_pages = int(float(soup1.select("#pagination option:last-child")[0]['value']))
    total_pages = int(soup1.select("#pagination option")[-1]['value'])
    # print(link)
    l1 = link.split("pg=2", 1)[0]
    l2 = link.split("pg=2", 1)[1]

    links = []
    for i in range(1, total_pages+1):
        print(i)
        link = f"{url}{l1}pg={i+1}{l2}"
        links.append(link)

    # print(links[0])


    ############Part 2: To get the link to all of the positions#############
    job_link = []

    front_link = 'https://www.jobstreet.com.sg'

    for i in range(1, len(links)):
        print(f"page{i}")
        r2 = requests.get(links[i])
        soup2 = bs(r2.content, features="html.parser")

        job_listing = soup2.find_all("h1", {"class": "z1s6m00 _1hbhsw64y y44q7i0 y44q7i3 y44q7i21 y44q7ii"})  ##REFER TO NO3###
        print(len(job_listing))
        # print(job_listing[0])
        for i in job_listing:
            # print(i.prettify())
            each_job_link = i.find("a")["href"]
            job_link.append(front_link + each_job_link)

    url_df = pd.DataFrame([job_link])
    url_df.to_csv('./url_file.csv', index=False)

    return job_link



def get_details(url):
    ##Load out first page
    r = requests.get(url)

    #Convert it to a beautiful soup object
    soup = bs(r.content,  features="html.parser")

    # Print out HTML
    # print(soup.prettify())

    ####Find the categorizal data of the web####
    body = soup.find_all("div", attrs={"class": "z1s6m00 _1hbhsw6r pmwfa50 pmwfa57"})
    job_list = {}

    for index, each in enumerate(body):

        try:
            each_title = each.find("span", attrs={"class": "z1s6m00 _1hbhsw64y y44q7i0 y44q7i3 y44q7i21 _1d0g9qk4 y44q7ia"}).get_text()
            # print(each_title)

            each_content = each.find("span", attrs={"class": "z1s6m00 _1hbhsw64y y44q7i0 y44q7i1 y44q7i21 _1d0g9qk4 y44q7ia"}).get_text()
            # print(each_content)
            job_list[each_title] = each_content

        except Exception as e:
            print(e)


    ####Find the name, body data of the web####
    main = soup.select(".z1s6m00._5135ge0._5135ge5 .z1s6m00._1hbhsw66q .z1s6m00")
    #since the class syntax is inconsistent from 1 link to another, only title is extracted;
    # the same thing go for the body of text since some says "Qualifications and Experience:" some says "Qualification"

    ####(",", strip=True) is super important because sometimes the different item of get test tend to stick together making hard to split later
    print(main[0].get_text(",", strip=True))
    job_title, company_name, *_ = main[0].get_text(",", strip=True).split(",")
    # print(job_title, company_name)


    jd = soup.select(".z1s6m00._1hbhsw66e ._1x1c7ng0 .z1s6m00._1hbhsw64y.y44q7i0.y44q7i1.y44q7i21.y44q7ii .z1s6m00")
    job_content = jd[0].get_text()
    # print(job_content)

    job_list["Job Title"] = job_title
    job_list[" Company"] = company_name
    job_list["Job Content"] = job_content

    return job_list


main_link = 'https://www.jobstreet.com.sg/data-scientist-jobs/in-Singapore?salary=5000&salary-max=6000'
jl = get_job_url(main_link)
print(jl)

# jl = ['https://www.jobstreet.com.sg/en/job/data-analysis-specialist-digital-e-commerce-%5Bid%3A-591082%5D-11059145?jobId=jobstreet-sg-job-11059145&sectionRank=62&token=0~68573293-de21-429b-be40-300e1af19ed5&fr=SRP%20Job%20Listing']

df = pd.DataFrame()

for each_link in jl:

    job_details = get_details(each_link)

    # dft = pd.DataFrame([title])
    # dfcom = pd.DataFrame([company])
    # dfcon = pd.DataFrame([content])
    # dflink = pd.DataFrame([each_link])
    df_cat = pd.DataFrame.from_dict(job_details, orient='index').T
    df_cat['url'] = each_link

    # df_1 = pd.concat([dft, dfcom, dfcon, dflink], axis=1, keys=['title','company', 'content', "url"])
    df = pd.concat([df, df_cat])

    pd.set_option('display.max_columns', None)
    print(df)
    print(df.columns)

df.to_csv("job_excel.csv", sep=',', index=False, encoding='utf-8')
