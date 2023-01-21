from deepawali import app
from flask_restful import Resource
from flask import request,jsonify
from deepawali.utils import get_domain_data, get_keyword_suggestions,related_keywords,get_page_content,get_keywords_from_text,get_site_links,get_response_code,get_keywords_of_an_url,historic_trends


class GetHistoricTrends(Resource):
    def post(self):
        try:
            data = request.get_json()
            keywords = data['keywords']
            country = data['country']
            historic_data = historic_trends(keywords,country)
            print(country)
            return jsonify({'data':historic_data})  
             
        except Exception as e:
            return jsonify(error=str(e))


class GetDomainData(Resource):
    def post(self):
        try:
            data = request.get_json()
            domains = data['domains']
            domain_data = get_domain_data(domains=domains)

            return jsonify({"domain_data":domain_data})  
             
        except Exception as e:
            return e

class GetKeywordSuggestions(Resource):
    def post(self):
        try:
            data = request.get_json()
            keyword = data['keyword']
            country = data['country']
            
            suggestions = get_keyword_suggestions(keyword, country)
            
            return jsonify({"suggestions":suggestions})

        except Exception as e:
            return e

class GetKeywordsFromText(Resource):
    def post(self):
        try:
            data = request.get_json()
            text = data['text']
            wordcount = data['word_count']
            duplication = data['duplication']
            max_keywords = data['max_keywords']
            
            keywords = get_keywords_from_text(text,wordcount,duplication,max_keywords)
            
            return jsonify(keywords)
        
        except Exception as e:
            return e

class GetRelatedKeywords(Resource):
    def post(self):
        try:
            data = request.get_json()
            keyword = data['keyword']
            
            keywords = related_keywords(keyword)

            return jsonify({"keywords": keywords})
        
        except Exception as e:
            return e

class GetKeywordsFromURL(Resource):
    def post(self):
        try:
            data = request.get_json()
            url = data['url']
            keyword_data = get_keywords_of_an_url(url)
            return jsonify(keyword_data)
        
        except Exception as e:
            return e

class GetBrokenLinks(Resource):
    def post(self):
        try:
            data = request.get_json()
            url = data['url']
            urls = get_site_links(url)
            return jsonify(urls)
        
        except Exception as e:
            return e  

class GetResponseCode(Resource):
    def post(self):
        try:
            data = request.get_json()
            url = data['url']
            res = get_response_code(url)
            return jsonify({"response_code":res})
        
        except Exception as e:
            return e 
            

