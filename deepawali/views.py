from deepawali import app
from flask_restful import Resource
from flask import request,jsonify
from deepawali.utils import get_domain_data, get_keyword_suggestions,extract_keywords,related_keywords,get_page_content


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
            
            keywords = extract_keywords(text,wordcount,duplication,max_keywords)
            
            return jsonify({"keywords": keywords})
        
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
            keyword_data = get_page_content(url)
            return jsonify(keyword_data)
        
        except Exception as e:
            return e

            

