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
from urllib.parse import urlparse
from tldextract import extract
from seoanalyzer import analyze
from nltk import ngrams
from nltk.corpus import stopwords
from collections import Counter
from pytrends.request import TrendReq
import pandas as pd 
import numpy as np
import time
from datetime import datetime, timedelta



def historic_trends(keyword,country):
    try:
        trend = TrendReq()
        keyword = [f"{keyword}"]        
        current_date = datetime.now()
        three_years_ago = current_date - timedelta(days=365*3)
        current_date_str = current_date.strftime("%Y-%m-%d")
        three_years_ago_str = three_years_ago.strftime("%Y-%m-%d") 

        trend.build_payload(kw_list=keyword,timeframe='{} {}'.format(three_years_ago_str,current_date_str),geo=country)    
        yearly_data = trend.interest_over_time()
        
        time.sleep(1)
        trend.build_payload(kw_list=keyword,timeframe='today 3-m',geo=country) 
        monthly_data = trend.interest_over_time()

        if(len(monthly_data.columns)==0):
            raise Exception("No Data Found")
        
        weekly_data = monthly_data

        weekly_data[keyword[0]] = weekly_data[keyword[0]].replace(0, np.nan)
        weekly_data[keyword[0]] = weekly_data[keyword[0]].fillna(method='bfill')

        monthly_data[keyword[0]] = monthly_data[keyword[0]].replace(0, np.nan)
        monthly_data[keyword[0]] = monthly_data[keyword[0]].fillna(method='bfill')

        yearly_data[keyword[0]] = yearly_data[keyword[0]].replace(0, np.nan)
        yearly_data[keyword[0]] = yearly_data[keyword[0]].fillna(method='bfill')

        data = yearly_data 

        monthly_data['month'] = monthly_data.index.month
        weekly_data['week'] =  weekly_data.index.week
        yearly_data['year'] =  yearly_data.index.year
        
        weekly_data = weekly_data.groupby(by='week').sum()
        monthly_data = monthly_data.groupby(by='month').sum()
        yearly_data = yearly_data.groupby(by='year').median()
        
        weekly_data['percentage_difference'] = (weekly_data[keyword[0]]-weekly_data[keyword[0]].shift(1))/weekly_data[keyword[0]].shift(1)*100
        monthly_data['percentage_difference'] = (monthly_data[keyword[0]]-monthly_data[keyword[0]].shift(1))/monthly_data[keyword[0]].shift(1)*100
        yearly_data['percentage_difference'] = (yearly_data[keyword[0]]-yearly_data[keyword[0]].shift(1))/yearly_data[keyword[0]].shift(1)*100
        
        weekly_data = weekly_data.reset_index()
        monthly_data = monthly_data.reset_index()
        yearly_data = yearly_data.reset_index()
        
        week_difference = str(round(weekly_data['percentage_difference'].iloc[-1]))
        monthly_difference = str(round(monthly_data['percentage_difference'].iloc[-1]))
        yearly_difference = str(round(yearly_data['percentage_difference'].iloc[-1] ))

        complete_data = {'three':three_years_ago_str,'current':current_date_str,'today_interest':str(data[keyword[0]].iloc[-1]),'daily_data' : {}, 'week_difference':week_difference,'monthly_difference':monthly_difference,'yearly_difference':yearly_difference,'keyword':keyword }
        
        
        data = data.reset_index()
        
        for index, row in data.iterrows():
            complete_data['daily_data'][row.date.strftime('%Y-%m-%d')] = round(row[keyword[0]])
        
        return complete_data

    except Exception as e:
        print(e)
        return []



def fetch_html(url):
    # Fetch the HTML content of the given URL
    response = requests.get(url)
    return response.text


def remove_comments(html):
    # Use a regular expression to remove the comments from the HTML content
    pattern = re.compile(r'<!--(.*?)-->', re.DOTALL)
    return pattern.sub('', html)


def extract_text(html):
    # Use BeautifulSoup to extract the text content from the HTML document
    soup = BeautifulSoup(html, 'html.parser')
    reply_elements = soup.find_all(class_='reply')
    # Remove the elements from the HTML document
    for element in reply_elements:
        element.extract()
    
    text = soup.get_text()
    return text

def is_not_letter(string):
    if len(string) == 1 and not string.isalpha():
        return True
    return False


def is_hindi(string):
    for char in string:
        if ord(char) >= 2304 and ord(char) <= 2431:
            return True
    return False

def preprocess_text(text):
    # Remove punctuation, convert to lowercase, and split into a list of words
    text = text.lower()
    text = text.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
    words = text.split()
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and not word.isnumeric() and not is_hindi(word) and not is_not_letter(word)]
    return words

def compute_keyword_densities(words, n=1):
    # Compute the densities of the individual words and n-grams in the list
    densities = {}
    if n == 1:
        # Compute the densities of individual words
        densities = Counter(words)
    else:
        # Compute the densities of n-grams
        ngrams_list = list(ngrams(words, n))
        densities = Counter(ngrams_list)
    return densities

def get_top_densities(densities, length, n=15):
    sorted_densities = sorted(densities.items(), key=lambda x: x[1], reverse=True)
    arr = []
    if length==1:
        for i in range(n):
            arr.append({sorted_densities[i][0]: int(sorted_densities[i][1])})
    else:
        for i in range(n):
            arr.append({' '.join(sorted_densities[i][0]): int(sorted_densities[i][1])})
    return arr

def get_url_data(url):
    print(urlparse('http://abc.hostname.com/somethings/anything/'))

def get_keywords_of_an_url(url):
    try:
        html = fetch_html(url)
        html = remove_comments(html)
        text = extract_text(html)
        words = preprocess_text(text)
        keywords = {'one':[],'two':[],'three':[]}
        for i in keywords:
            if i=='one':
                densities = compute_keyword_densities(words, n=1)
                updated_densities = get_top_densities(densities, 1, 15)  # Set n to the length of the n-grams you want to compute
                keywords[i] = updated_densities
            elif i=='two':
                densities = compute_keyword_densities(words, n=2)
                cleaned_densities_two = get_top_densities(densities, 2, 15)
                keywords[i] = cleaned_densities_two
                    
            else:
                densities = compute_keyword_densities(words, n=3)
                cleaned_densities_three = get_top_densities(densities, 3, 15)
                keywords[i] = cleaned_densities_three
    except Exception as e:
        print(e)
        return []
    return keywords


def get_response_code(url):
    headers = {'Access-Control-Allow-Origin': '*'}
    response = requests.get(url, headers=headers)
    reason = response.reason
    response_code = response.status_code
    
    return response_code

def is_internal(url, link):
    base_url = urlparse(url).netloc

    href = link.get('href')
    if (href and urlparse(href).netloc == base_url) or href=='#':
        return True
    elif href:
        return False


def is_no_follow(link):

    rel = link.get('rel')
    
    if rel!=None and 'nofollow' in rel:
        return True
    else:
        return False

def get_site_links(url):
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        urls = []
        internal_flag = 0
        external_flag = 0

        dofollow_count = 0
        nofollow_count = 0

        total_cnt = len(links)

        for link in links:
            data = dict()
            try:
                if link.get('href').startswith('https') or link.get('href').startswith('http'):
                    data['url'] = link.get('href')
                    data['text'] = link.text
                    internal = is_internal(url, link)

                else:
                    if "#" in link.get('href'):
                        if url[-1]=='/':
                            data['url'] = url+link.get('href').replace('/','')
                        else:
                            data['url'] = url+'/'+link.get('href').replace('/','')
                    else:
                        data['url'] = url

                    if 'comment' in link.get('href').lower():
                        data['text'] = 'Reply'
                    else:
                        data['text'] = ''
                    internal = True
                
                if internal:
                    internal_flag +=1
                else:
                    print(link.get('href'))
                    external_flag+=1
                data['internal'] = internal
                
                no_follow = is_no_follow(link)
                if no_follow:
                    nofollow_count+=1
                else:
                    dofollow_count+=1
                data['no_follow'] = no_follow
 
                urls.append(data)
            except Exception as e:
                print(e)
                continue
 
        return {"urls":urls, "internalLinks":internal_flag, "externalLinks":external_flag, "no_follow":nofollow_count, "do_follow":dofollow_count, "total_cnt":total_cnt }
    except Exception as e:
        print(e,'--------')
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
        
        output = ''
        blacklist = [
            'comment -##'
            '[document]',
            'noscript',
            'header',
            'html',
            'meta',
            'head', 
            'input',
            'script',
            'style',
            'input'
        ]
        for t in text:
            if t.parent.name not in blacklist:
                output += t.replace("\n","").replace("\t","")

        keywords = extract_keywords(output, 1, 0.9, 100)
        
        updated_keywords = dict()
        updated_keywords['one'] = []
        updated_keywords['two'] = []
        updated_keywords['three'] = []

        for i in keywords:
            
            if detectlanguage(i[0],False)=='en':

                word_len = len(i[0].split())
                if word_len==1:
                    updated_keywords['one'].append({i[0]: 1 if text.count(i[0])==0 else output.count(i[0])})
                elif word_len==2:
                    updated_keywords['two'].append({i[0]: 1 if text.count(i[0])==0 else output.count(i[0])})
                elif word_len==3:
                    updated_keywords['three'].append({i[0]: 1 if text.count(i[0])==0 else output.count(i[0])})
            
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    with HTMLSession() as session:
        try:
            
            res = requests.get(url,headers=headers)
            html_page = res.content

            soup = BeautifulSoup(html_page, 'html.parser')
            text = soup.find_all(text=True)
            return text_cleaning(text)
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
    
    

    
