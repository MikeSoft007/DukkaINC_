from flask import request, make_response, jsonify, send_file
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

        
        filename = "Receipt.html"
        #save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Desktop')
        save_path = os.path.join(os.path.expanduser('~'), './Desktop')
        complete_name = os.path.join(save_path, filename)
        file1 = open(complete_name, "w+")
        file1.write('''
        <table>
  <tr>
    <th>Name.</th>
    <th>Address</th>
    <th>Phone</th>
    <th>Amount</th>
    <th>Date</th>
    <th>Reference</th>
  </tr>
  <tr>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
    <td>{}</td>
  </tr>
</table>
        
        '''.format(getRef['name'],getRef['address'], getRef['phone_number'], getRef['amount'], getRef['date'], getRef['transaction_ref'])
            
    )

        return jsonify({"message": "Receipt downloaded in /Desktop", "status": 200})

api.add_resource(Downloads, '/download/<string:ref>')