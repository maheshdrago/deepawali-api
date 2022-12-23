import whois
from datetime import datetime,date
from dateutil import relativedelta
import socket
import requests
from bs4 import BeautifulSoup    
from langdetect import detect                       
import iso639  
import yake
from pytrends.request import TrendReq
from rake_nltk import Rake
from requests_html import HTMLSession
import re
from multiprocessing.pool import ThreadPool


def get_response_code(url):
    response_code = requests.get(url).status_code

    return response_code

    

def get_site_links(url):
    try:
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        
        urls = []
        for link in soup.find_all('a'):
            flag = re.findall('^http|https.*',link.get('href'))
            if flag:
                urls.append(link.get('href'))
        return urls
    except Exception as e:
        print(e)
        return []



def extract_keywords(text, wordcount, duplication, max_keywords):
    """
    Extract keywords from a given text and given parameter with
    :param text: inserted text from textbox
    :param wordcount: limit the word count of the extracted keyword, i.e. <= 3
    :param duplication: limit the duplication of words in different keywords. 0.9 allows repetition of words in keywords
    :param max_keywords: determine the count of keywords which are extracted, i.e. <= 20
    :return: list of tuples keywords with scores
    """
    try:
        language = detectlanguage(text, False)
        extractor = yake.KeywordExtractor(
            lan=language,
            n=wordcount,
            dedupLim=duplication,
            top=max_keywords,
            features=None
        )
        keywords = extractor.extract_keywords(text)
        keywords.sort(key=lambda a: a[1])      # Lower Score = the more relevant. For this: Sorting list of tuples of Item 1

        return keywords
    except Exception as e:
        return []



def text_cleaning(text):
    try:
        text = re.sub(r'[\n\r]+', '\n', text)
        keywords = extract_keywords(text, 4, 0.9, 100)
        updated_keywords = dict()
        updated_keywords['one'] = []
        updated_keywords['two'] = []
        updated_keywords['three'] = []

        for i in keywords:
            
            if detectlanguage(i[0],False)=='en':

                word_len = len(i[0].split())
                if word_len==1:
                    updated_keywords['one'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
                elif word_len==2:
                    updated_keywords['two'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
                elif word_len==3:
                    updated_keywords['three'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
            
        return updated_keywords

    except Exception as e:
        print(e)
        return dict()


def get_keywords_from_text(text,wordcount, duplication, max_keywords):
    try:
        keywords = extract_keywords(text,wordcount, duplication, max_keywords)
        updated_keywords = dict()
        updated_keywords['one'] = []
        updated_keywords['two'] = []
        updated_keywords['three'] = []

        for i in keywords:
            
            if detectlanguage(i[0],False)=='en':

                word_len = len(i[0].split())
                if word_len==1:
                    updated_keywords['one'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
                elif word_len==2:
                    updated_keywords['two'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
                elif word_len==3:
                    updated_keywords['three'].append({i[0]: 1 if text.count(i[0])==0 else text.count(i[0])})
            
        return updated_keywords
    
    except Exception as e:
        print(e)
        return {}
    
def get_page_content(url):
    print("get_page_content")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    with HTMLSession() as session:
        try:
            res = session.get(url, headers=headers, timeout=200)
            return text_cleaning(BeautifulSoup(res.content, 'html.parser').text)
        except Exception as e:
            print(e)
            return text_cleaning(BeautifulSoup('', 'html.parser').text)



def detectlanguage(text, short: bool):
    if short:                                       
        language = iso639.to_name(detect(text))
    else:
        language = detect(text)
    return language

def related_keywords(keyword):
    trend = TrendReq()
    keyword = [f"{keyword}"]             
    trend.build_payload(kw_list=keyword)    
    related_kw = trend.related_topics()
    related_kw.values()
    data_top_kw = list(related_kw.values())[0]["top"]
    list_top_kw = []
    for i in range(len(data_top_kw.values)):
        list_top_kw.append(data_top_kw.values[i][5])

    return list_top_kw




def get_age(creation_date):
    if(isinstance(creation_date,list)):
        creation_date = creation_date[0]
    
    start_date_year = creation_date.strftime("%Y")
    start_date_month = creation_date.strftime("%m")
    start_date_day = creation_date.strftime("%d")
    start_date = start_date_day+'/'+start_date_month+'/'+start_date_year
        
    end_date_year = date.today().strftime("%Y")
    end_date_month = date.today().strftime("%m")
    end_date_day = date.today().strftime("%d")
    end_date = end_date_day+'/'+end_date_month+'/'+end_date_year

    start_date = datetime.strptime(start_date, "%d/%m/%Y")
    end_date = datetime.strptime(end_date, "%d/%m/%Y")

    delta = relativedelta.relativedelta(end_date, start_date)
    return str(delta.years)+' Years '+str(delta.months)+' months '+str(delta.days)+' days'


def is_registered(domain_name):
    try:
        w = whois.whois(domain_name)
    except Exception as e:
        return False
    else:
        return bool(w.domain_name)


def get_domain_data(domains):
    domain_list = []
    for domain_name in domains:
        domain_data = dict()
        if is_registered(domain_name):
            whois_info = whois.whois(domain_name)
            domain_data[domain_name] = {}

            try:
                domain_data[domain_name]['registrar'] = whois_info.registrar
            except:
                domain_data[domain_name]['registrar'] = 'N/A'

            try:
                if(isinstance(whois_info.creation_date,list)):
                    temp = whois_info.creation_date[0]
                    domain_data[domain_name]['creation_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
                else:
                    temp = whois_info.creation_date
                    domain_data[domain_name]['creation_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
            except:
                domain_data[domain_name]['creation_date'] = 'N/A'

            domain_data[domain_name]['age'] = get_age(whois_info.creation_date)

            try:
                if(isinstance(whois_info.expiration_date,list)):
                    temp = whois_info.expiration_date[0]
                    domain_data[domain_name]['expiration_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
                else:
                    temp = whois_info.expiration_date
                    domain_data[domain_name]['expiration_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
            except:
                domain_data[domain_name]['expiration_date'] = "N/A"

            try:
                if(isinstance(whois_info.updated_date,list)):
                    temp = whois_info.updated_date[0]
                    domain_data[domain_name]['updated_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
                else:
                    temp = whois_info.updated_date
                    domain_data[domain_name]['updated_date'] = temp.strftime("%d")+'-'+temp.strftime("%m")+'-'+temp.strftime("%Y")
            except:
                domain_data[domain_name]['updated_date'] = 'N/A'

            try:
                if(isinstance(whois_info.name_servers,list)):
                    domain_data[domain_name]['name_servers'] = whois_info.name_servers[0]
                else:
                    domain_data[domain_name]['name_servers'] = whois_info.name_servers
            except:
                domain_data[domain_name]['name_servers'] = ""

            try:
                domain_data[domain_name]['ip_address'] = socket.gethostbyname(domain_name)
            except:
                domain_data[domain_name]['ip_address'] = 'N/A'

            domain_data[domain_name]['archive'] = 'https://web.archive.org/web/20220000000000*/'+domain_name
        else:
            domain_data[domain_name] = 'Not Registered'
        
        domain_list.append(domain_data)
    return domain_list


def get_keyword_suggestions(keyword, country):
    sugg_all = {}
    questions = ['When','What','Where','How','Why','Who','Which','Will','Can','Does','Is','Are','Do']

    for question in questions:
        kw = ' '.join([question, keyword])

        r = requests.get('http://suggestqueries.google.com/complete/search?output=toolbar&hl={}&q={}'.format(country,kw))
        soup = BeautifulSoup(r.content, 'html.parser')
        sugg = [sugg['data'] for sugg in soup.find_all('suggestion')]

        sugg_all[question] = sugg
        
    return sugg_all
    
    
