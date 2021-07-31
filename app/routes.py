from flask import request, make_response, jsonify, send_file
from app import app, api, mongo
from app.utils import DumpData
from flask_restful import Resource, reqparse
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


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
                                    data['price'], data['item'], data['qty'], data['price']*data['qty'])

        return jsonify(
            {
                "Message": "Receipt successfully generated kindly y go to /download endpoint to download receipt",
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

        # data which we are going to display as tables
        DATA = [
            ["Date", "Name", "Item", "Qty", "Amount payable (NGN.)", "Address", "Phone"],
            [
                getRef['date'],
                getRef['name'],
                getRef['item'],
                getRef['qty'],
                getRef['amount'],
                getRef['address'],
                getRef['phone_number']
            ],
        ]

        # creating a Base Document Template of page size A4
        pdf = SimpleDocTemplate("receipt.pdf", pagesize=A4)

        # standard stylesheet defined within reportlab itself
        styles = getSampleStyleSheet()

        # fetching the style of Top level heading (Heading1)
        title_style = styles["Heading1"]

        # 0: left, 1: center, 2: right
        title_style.alignment = 1

        # creating the paragraph with
        # the heading text and passing the styles of it
        title = Paragraph("DukkaINC", title_style)

        # creates a Table Style object and in it,
        # defines the styles row wise
        # the tuples which look like coordinates
        # are nothing but rows and columns
        style = TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("GRID", (0, 0), (4, 4), 1, colors.black),
                ("BACKGROUND", (0, 0), (3, 0), colors.gray),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ]
        )

        # creates a table object and passes the style to it
        table = Table(DATA, style=style)

        # final step which builds the
        # actual pdf putting together all the elements
        lsr = pdf.build([title, table])
        return send_file("/"+lsr, as_attachment=True)
        #return jsonify ({"message": "Receipt successfully downloaded", "status": 200})

api.add_resource(Downloads, '/download/<string:ref>')