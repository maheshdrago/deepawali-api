from deepawali import app
from flask_restful import Resource
from flask import request,jsonify
from deepawali.utils import get_domain_data

class GetDomainData(Resource):
    def post(self):
        try:
            data = request.get_json()
            domains = data['domains']
            domain_data = get_domain_data(domains=domains)
            return jsonify({"domain_data":domain_data})   
        except Exception as e:
            print(e)

