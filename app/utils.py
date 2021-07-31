# Import statement
from app import mongo
from flask import jsonify
from datetime import datetime, date, timedelta
import requests, uuid, os
import uuid

# mongo collection
mongo_data = mongo.db.reciept

#funtion to get current date and time for transaction
def nigerian_time():
    now = datetime.utcnow() + timedelta(hours=1)
    today = date.today()
    d2 = today.strftime("%Y-%m-%d")
    tm = now.strftime("%H:%M:%S%p")
    return d2 + ' ' + 'at' + ' ' + tm

# class to get all user data before confirming transaction
class DumpData:

    # def __init__(self, phone):
    #     self.phone = phone

    def send_data(self, name, address, phone, price, item, qty, amount):
        lis = []
        refs = str(uuid.uuid4().int)[:10]
        lis.append(refs)
        token = lis[0]
        payload2 = {
            "name": name,
            "address": address,
            "phone_number": phone,
            "item": item,
            "qty": qty,
            "price":price,
            "amount": amount,
            "transaction_ref": token,
            "date":nigerian_time()
        }
        mongo_data.insert(payload2)
