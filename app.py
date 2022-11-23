from deepawali import app
from deepawali import views
from deepawali.views import GetDomainData
from flask_restful import Api
from flask_cors import CORS

cors = CORS(app)
api = Api(app)

api.add_resource(GetDomainData, '/domainData')

if __name__ == '__main__':
    app.run(debug=True)
