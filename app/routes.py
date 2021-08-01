from flask import request, make_response, jsonify, send_from_directory
from flask_csv import send_csv
from app import app, api, mongo
from app.utils import DumpData
from flask_restful import Resource, reqparse
import os
import uuid


#geerate unique transcation ref
lis = []
refs = str(uuid.uuid4().int)[:10]
lis.append(refs)
token = lis[0]

@app.route('/', methods=['POST', 'GET'])
def index():
    response = make_response("Test connection ok!")
    response.headers['Content-Type'] = "text/plain"
    return response


class Generate(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('address', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('phone_number', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('price', type=int, required=True, help="This cannot be left blank")
    parser.add_argument('item', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('qty', type=int, required=True, help="This cannot be left blank")

    

    def post(self):
        data = Generate.parser.parse_args()
        if data['price'] < 1 or data['qty'] < 1:
            return jsonify({"message": "Enter correct vale for price or quantity"})

        pushData = DumpData()
        pushData.send_data(data['name'], data['address'], data['phone_number'],
                                    data['price'], data['item'], data['qty'], data['price']*data['qty'], token)

        return jsonify(
            {
                "Message": "Receipt successfully generated REFERENCE: {} kindly use the generated ref and go to /download endpoint to download receipt".format(token),
                "status":200
            }
        )


api.add_resource(Generate, '/generate')


class Downloads(Resource):
    def post(self, ref):

        getRef = mongo.db.reciept.find_one({"transaction_ref": ref})
        if not getRef :
            return jsonify({"message": "Invalid Refernce number"})
        if ' '.join(ref.split()) == '':
            return jsonify({"message": "Please enter transaction reference number to download reciept"})
        c = []
        c.append({"Name":getRef['name'], "Address":getRef['address'], "Phone":getRef['phone_number'], "Amount":getRef['amount'], "Date":getRef['date'], "Transaction_Ref":getRef['transaction_ref']}) 

        send_csv(c, "Receipt.csv", ["Name", "Address", "Phone", "Amount", "Date", "Transaction_Ref"])

   
api.add_resource(Downloads, '/download/<string:ref>')