from flask import request, make_response, jsonify, url_for, render_template
from flask_csv import send_csv
from app import app, api, mongo
from app.utils import DumpData
from flask_restful import Resource, reqparse
import os, subprocess, platform
import uuid
import pdfkit
from functools import wraps



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


def require_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('x-offense-key') and request.args.get('x-dukka-key') == os.environ.get('DUKKA_KEY'):
            return view_function(*args, **kwargs)
        else:
            return make_response(jsonify({"message": "Unauthorized users access at " + request.url, "status": False}), 403)
    return decorated_function




class Generate(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('address', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('phone_number', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('price', type=int, required=True, help="This cannot be left blank")
    parser.add_argument('item', type=str, required=True, help="This cannot be left blank")
    parser.add_argument('qty', type=int, required=True, help="This cannot be left blank")

    
    @require_key
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


    def get(self, ref):
        getRef = mongo.db.reciept.find_one({"transaction_ref": ref})

        if not getRef :
            return jsonify({"message": "Invalid Refernce number"})

        if ' '.join(ref.split()) == '':
            return jsonify({"message": "Please enter transaction reference number to download reciept"})

        if platform.system() == 'Windows':
            pdfkit_config = pdfkit.configuration( wkhtmltopdf=os.environ.get('WKHTMLTOPDF_PATH', 'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'))
        else:
            WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_PATH', '/app/bin/wkhtmltopdf')], stdout=subprocess.PIPE).communicate()[0].strip()
            pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
        
        name = getRef['name'] 
        address = getRef['address'] 
        phone = getRef['phone_number']
        amount = getRef['amount']
        date = getRef['date'] 
        item = getRef['item']
        ref = getRef['transaction_ref']
        qty = getRef['qty']

        html = render_template("report.html", name=name, address=address, phone =phone, amount=amount, date=date, ref=ref, item=item, qty=qty)
        pdf = pdfkit.from_string(html, False, configuration=pdfkit_config)
        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "inline; filename=output.pdf"
        return response
    

api.add_resource(Downloads, '/download/<string:ref>')