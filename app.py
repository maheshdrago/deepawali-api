from deepawali import app
from deepawali import views
from deepawali.views import GetDomainData, GetKeywordSuggestions, GetKeywordsFromText, GetRelatedKeywords, GetKeywordsFromURL
from flask_restful import Api
from flask_cors import CORS

cors = CORS(app)
api = Api(app)

api.add_resource(GetDomainData, '/domainData')
api.add_resource(GetKeywordSuggestions, '/keywordSuggestions')
api.add_resource(GetKeywordsFromText, '/keywordsFromText')
api.add_resource(GetRelatedKeywords, '/relatedKeywords')
api.add_resource(GetKeywordsFromURL, '/getKeywordsFromUrl')

if __name__ == '__main__':
    app.run(debug=True)
