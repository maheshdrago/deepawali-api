from deepawali import app
from deepawali import views
from deepawali.views import GetDomainData, GetKeywordSuggestions, GetKeywordsFromText, GetRelatedKeywords, GetKeywordsFromURL,GetBrokenLinks,GetResponseCode, GetHistoricTrends
from flask_restful import Api
from flask_cors import CORS



api = Api(app)
CORS(app)

api.add_resource(GetDomainData, '/domainData')
api.add_resource(GetKeywordSuggestions, '/keywordSuggestions')
api.add_resource(GetKeywordsFromText, '/keywordsFromText')
api.add_resource(GetRelatedKeywords, '/relatedKeywords')
api.add_resource(GetKeywordsFromURL, '/getKeywordsFromUrl')
api.add_resource(GetBrokenLinks, '/getBrokenlinks')
api.add_resource(GetResponseCode, '/getResponseCode')
api.add_resource(GetHistoricTrends, '/historicData')


if __name__ == '__main__':
    app.run(debug=True)
