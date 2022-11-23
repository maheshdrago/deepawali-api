import whois
from datetime import datetime,date
from dateutil import relativedelta
import socket


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
    
