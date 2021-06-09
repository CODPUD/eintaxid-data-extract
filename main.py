import requests
from bs4 import BeautifulSoup
import string, csv
import re, math

chars = string.ascii_uppercase + string.digits

URL = "https://eintaxid.com"

# def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
#     percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
#     filledLength = int(length * iteration // total)
#     bar = fill * filledLength + '-' * (length - filledLength)
#     print(f'\r{prefix} |{bar}| {percent}% {suffix}', end="")
#     if iteration == total:
#         print()

def get_text(link=""):
    r = requests.get(URL + link)
    return r.text

def get_companies_link():
    for c in chars:
        #print(f"Parsing companies {c}:")
        text = get_text(f"/companies/{c}/")
        count = math.ceil(int(re.search(r'[0-9]* companies found', text).group(0).split()[0]) / 20)
        for i in range(count):
            try:
                #printProgressBar(i, count, f"Progress [{c}]:", "Complete")
                text = get_text(f"/companies/{c}/?page={i}")
                soup = BeautifulSoup(text, 'lxml')
                soups = soup.find_all(class_="panel panel-default pan")
                for s in soups:
                    print('\r' + f"Company[{c}]: parsed {i}/{count} pages", end="")
                    soup = s.find("a", class_='question')
                    if soup:
                        yield soup['href']
            except:
                continue

def get_company_info(link):
    text = get_text(link)
    soup = BeautifulSoup(text, 'lxml')

    dict = {}

    try:
        dict["company_description"] = soup.find("div", class_="panel-body").text.split("\n")[5]
    except:
        pass

    all_details = soup.find_all("table", class_="table table-striped")
    try:
        basic_details = all_details[0].find_all('td')

        dict["organization_name"] = basic_details[0].text
        dict["irs_ein"] = basic_details[1].text
        dict["doing_business_as"] = basic_details[2].text
        dict["type_of_business"] = basic_details[3].text
    except:
        pass

    try:
        business_details = all_details[1].find_all('td')

        dict["business_phone"] = business_details[0].text
        dict["business_address"] = business_details[1].text
        dict["business_city"] = business_details[2].text
        dict["business_state"] = business_details[3].text
        dict["business_zip"] = business_details[4].text
    except:
        pass

    try:
        mailing_details = all_details[2].find_all('td')

        dict["mailing_address"] = mailing_details[0].text
        dict["mailing_city"] =  mailing_details[1].text
        dict["mailing_state"] = mailing_details[2].text
        dict["mailing_ZIP"] =  mailing_details[3].text
    except:
        pass

    try:
        incorporation_details = all_details[3].find_all('td')

        dict["central_index_key"] = incorporation_details[0].text
        dict["end_of_fiscal_year"] = incorporation_details[1].text
        dict["incorporation_state"] = incorporation_details[2].text
        dict["incorporation_sub_division"] = incorporation_details[3].text
        dict["incorporation_country"] = incorporation_details[4].text
        dict["filling_year"] = incorporation_details[5].text
    except:
        pass

    return dict

def csv_writer(data):
    with open('data.csv', 'a', newline="") as f:  # You will need 'wb' mode in Python 2.x
        w = csv.writer(f)
        w.writerow(data.values())

if __name__ == '__main__':
    print("Started")
    data = get_companies_link()
    print("Getting Companies Link...")
    for c in data:
        info = get_company_info(c)
        csv_writer(info)
