#!C:\Python310\python.exe -u

from django.shortcuts import render
import uuid
import json
import datetime
import requests
import sys
from time import gmtime, strftime
from atompay.AESCipher import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import cgi
import binascii
from hashlib import pbkdf2_hmac
# Create your views here.

@csrf_exempt
def payview(request):

    print("payview called")

    amount = '10.00'
    merchTxnId = uuid.uuid4().hex[:12]
    merchId = '317159'
    password = 'Test@123'
    product = 'NSE'
    custEmail = 'test@atomtech.in'
    custMobile = '8956895878'
    returnUrl = 'http://127.0.0.1:8000/response/'
    txnDate = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    jsondata = '{ "payInstrument": { "headDetails": { "version": "OTSv1.1", "api": "AUTH", "platform": "FLASH" }, "merchDetails": { "merchId": "'+str(merchId)+'", "userId": "", "password": "'+str(password)+'", "merchTxnId": "'+str(merchTxnId)+'", "merchTxnDate": "'+str(txnDate)+'" }, "payDetails": { "amount": "'+str(amount)+'", "product": "'+str(product)+'", "custAccNo": "213232323", "txnCurrency": "INR" }, "custDetails": { "custEmail": "'+str(custEmail)+'", "custMobile": "'+str(custMobile)+'" }, "extras":{ "udf1":"udf1", "udf2":"udf2", "udf3":"udf3", "udf4":"udf4", "udf5":"udf5"} } }'
    print("jsondata")
    print(jsondata)

    cipher = AESCipher('self')
    encrypted = cipher.encrypt(bytes(jsondata, encoding="raw_unicode_escape"))

    url = "https://caller.atomtech.in/ots/aipay/auth"
    payload = "encData="+encrypted+"&merchId="+str(merchId)
    payload = {'encData':encrypted, 'merchId':str(merchId)}
    headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }
    
    cafile = 'atompay/cacert.pem'
    response = requests.post(url, data=payload, headers=headers, verify=cafile)
    print("Data")
    print(response.text)

    arraySplit = response.text.split('&')
    arraySplitTwo = arraySplit[1].split('=')
    decrypted = cipher.decrypt(arraySplitTwo[1])
    json_string = decrypted.replace("", " ")
    y = json.loads(json_string)
    atomTokenId = y['atomTokenId']
    print("AtomTokenId")
    print(atomTokenId)
   
    return render(request, "base.html", {'atomTokenId' : atomTokenId, 'merchId' : merchId, 'custEmail' : custEmail,  'custMobile' : custMobile, 'returnUrl' : returnUrl , 'amount' : amount, 'merchTxnId' : merchTxnId})


@csrf_exempt
def resp(request): 
    
    if request.method == 'POST':
     rawData= request.POST["encData"]
     
    reskey = 'KEYRESP123657234'
    print(rawData)
    cipher = AESCipher('self')
    decrypted = cipher.decrypt(rawData)

    jstring = decrypted
    decodedData = json.loads(jstring)

    # # In below response ['payInstrument']['responseDetails']['statusCode'] is important to know if payment status is success or fail. You can redirect users to your custom Js page accordingly.
    if decodedData['payInstrument']['responseDetails']['statusCode'] == "OTS0000":
       
        print("All Response Data:")
        print(decodedData)

        transactiondate = decodedData['payInstrument']['merchDetails']['merchTxnDate']
        banktransactionid = decodedData['payInstrument']['payModeSpecificData']['bankDetails']['bankTxnId']
        
        # /* Signature Validation */
        # //merchantId + atomTxnId + merchantTxnId + Total amount + responseCode + subChannel + bankTxnId
        respsignature = decodedData['payInstrument']['payDetails']['signature']
        merchantId =  str(decodedData['payInstrument']['merchDetails']['merchId'])
        atomTxnId = str(decodedData['payInstrument']['payDetails']['atomTxnId'])
        merchantTxnId = str(decodedData['payInstrument']['merchDetails']['merchTxnId'])
        amount =  decodedData['payInstrument']['payDetails']['totalAmount']
        Total_amount = "{:.2f}".format(amount)
        resultcode = str(decodedData['payInstrument']['responseDetails']['statusCode'])
        subChannel =  str(decodedData['payInstrument']['payModeSpecificData']['subChannel'][0])
        bankTxnId=  str(decodedData['payInstrument']['payModeSpecificData']['bankDetails']['bankTxnId'])

        sig_str = merchantId+atomTxnId+merchantTxnId+Total_amount+resultcode+subChannel+bankTxnId
        final_cret_sign = hmac.new(reskey.encode('UTF-8'), sig_str.encode('UTF-8'), hashlib.sha512).hexdigest()

        signature_validation = ""
        
        if respsignature == final_cret_sign:
            signature_validation = "Transaction success, Signature valid!"
            print(signature_validation)
        else:
            signature_validation = "Transaction Failed, Signature invalid!"
            print(signature_validation)

        # /* Signature Validation End */

          

        print("Test:"+ sig_str)
        print("final_cret_sign:"+ final_cret_sign)
        print("Transaction Result : " + resultcode)
        print("Merchant Transaction Id : " + merchantId)
        print("Transaction Date : " + transactiondate)
        print("Bank Transaction Id : " + banktransactionid)
        print("Response Signature : " + respsignature)
        
    else:   
        print("Payment failed, Please try again.. <br>")

    return render(request, "response.html", {
         'resultcode': resultcode,
         'merchantid': merchantId,
         'transactiondate': transactiondate,
         'banktransactionid': banktransactionid,
         'signature_validation': signature_validation,
         'finalresp': decodedData
        })