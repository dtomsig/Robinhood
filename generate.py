#!/usr/bin/python3 

import datetime, os, requests, stock_record

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

username             = input("\nEnter your Robinhood username: ") 
password             = input("Enter your Robinhood password: ")
earliest_date        = input("Enter the earliest date of transaction data " +
                             "for import [Format: yyyy-mm-dd)]: ")
authentication_entry = input("Do you have an authenticator (y/n): ")

                         
login_data = {"username" : username, "password" : password} 
if(authentication_entry == "y"):
    requests.post("https://api.robinhood.com/api-token-auth/", login_data)
    mfa_code = input("Enter mfa code (SMS currently only supported): ")
    login_data = {"username" : username, "password" : password, 
                  "mfa_code" : mfa_code}

session_token = requests.post("https://api.robinhood.com/api-token-auth/", 
                              login_data).json()["token"]
                                                                     
header = {"Authorization" : "Token " + session_token}

account_data = requests.get("https://api.robinhood.com/accounts/", 
                            headers = header).json()
dividend_data = requests.get("https://api.robinhood.com/dividends/", 
                             headers = header).json()
order_data = requests.get("https://api.robinhood.com/orders/", headers = 
                          header).json()
                          
#3. Begin file generatione. 
stock_record = stock_record.Stock_Record()
transaction_file = open("./output_files/transactions.qif", "w+")
securities_file = open("./output_files/securities.ofx", "w+")
instrument_id_list = []

transaction_file.write("!Account\n")
transaction_file.write("NRobinhood Brokerage Account\n")
transaction_file.write("TInvst\n")
transaction_file.write("^\n")
transaction_file.write("!Type:Invst\n")

#4. Cycle through order data.

for order in reversed(order_data["results"]):
	
    if(order["state"] != "filled"):
        continue         
        
    fee                  = order["fees"]
    instrument_data      = requests.get(order["instrument"]).json()
    instrument_id        = (order["instrument"]
                           .split("https://api.robinhood.com/instruments/")[1]
                           .replace("/", ""))
    order_side           = order["side"]
    price                = order["executions"][0]["price"]        
    quantity             = order["executions"][0]["quantity"]
    raw_date             = datetime.datetime.strptime(order["updated_at"],
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
    stock_name           = instrument_data["name"]
    transaction_date     = str(raw_date).split("T")[0]

    instrument_id_list.append(instrument_id)  
    
    if(order_side == "buy"):
        stock_record.add_stock(stock_name, transaction_date, float(quantity), 
                               float(price))
        if(transaction_date < earliest_date):
            continue
        transaction_file.write("NBuy\n")
        transaction_file.write("Y" + stock_name + "\n")
        transaction_file.write("D" + transaction_date + "\n") 
        transaction_file.write("Q" + quantity + "\n")
        transaction_file.write("I" + price + "\n")
        transaction_file.write("T" + str(float(quantity) * float(price)) + "\n")
        transaction_file.write("^\n")        
                               
    if(order_side == "sell"):
        sale_data = stock_record.sell_stock(stock_name, transaction_date, 
                                            float(quantity), float(price))
                                            
        num_short_term       = sale_data["num_short_term"]
        short_term_gain      = sale_data["short_term_gain"]
        num_long_term        = sale_data["num_long_term"]
        long_term_gain       = sale_data["long_term_gain"]
        
        if(transaction_date < earliest_date):
            continue

        transaction_file.write("NSell\n")
        transaction_file.write("Y" + stock_name + "\n")
        transaction_file.write("D" + transaction_date + "\n") 
        transaction_file.write("Q" + quantity + "\n")
        transaction_file.write("I" + price + "\n")
        transaction_file.write("O" + fee + "\n")
        transaction_file.write("T" + str(float(quantity) * float(price) - 
                                          float(fee)) + "\n")
        transaction_file.write("^\n")
        
        if(num_short_term > 0):
            transaction_file.write("NCGShort\n")             
            transaction_file.write("Y" + stock_name + "\n")
            transaction_file.write("D" + transaction_date + "\n")     
            transaction_file.write("T" + str(short_term_gain) + "\n")
            transaction_file.write("^\n")   

        if(num_long_term > 0):
            transaction_file.write("NCGLong\n")             
            transaction_file.write("Y" + stock_name + "\n")
            transaction_file.write("D" + transaction_date + "\n")     
            transaction_file.write("T" + str(long_term_gain) + "\n")
            transaction_file.write("^\n")   

#5. Obtain dividend data, reversed to have the earliest print first.
for dividend in reversed(dividend_data["results"]):
    if(dividend["paid_at"] == None):
        continue
    else:
        raw_date = datetime.datetime.strptime(dividend["paid_at"],
                                              "%Y-%m-%dT%H:%M:%S.%fZ")
        local_date = raw_date.replace(tzinfo = datetime.timezone.utc) \
                     .astimezone(tz = None)
        dividend_date = str(local_date).split(" ")[0]
        
    if(dividend_date < earliest_date):
        continue 
        
    dividend_amount      = dividend["amount"] 
    instrument_data      = requests.get(dividend["instrument"]).json()
    instrument_name      = instrument_data["name"] 
    
    transaction_file.write("NDiv\n")
    transaction_file.write("Y" + instrument_name + "\n")
    transaction_file.write("D" + dividend_date + "\n") 
    transaction_file.write("T" + dividend_amount + "\n")
    transaction_file.write("^\n")
    exit(0)

securities_file.write("<OFX>\n")
securities_file.write("<SECLISTMSGSRSV1>\n")
securities_file.write("<SECLIST>\n")
for instrument_id in list(set(instrument_id_list)):
    instrument_data = requests.get("https://api.robinhood.com/instruments/" +
                                   instrument_id , headers = header).json()
                                   
    instrument_name      = instrument_data["name"]  
    instrument_symbol    = instrument_data["symbol"]  
    
    securities_file.write("<STOCKINFO>\n")
    securities_file.write("<SECINFO>\n")
    securities_file.write("<SECID>\n")
    securities_file.write("<UNIQUEID>\n")
    securities_file.write(instrument_id + "\n")
    securities_file.write("</UNIQUEID>\n")
    securities_file.write("<UNIQUEIDTYPE>\n")
    securities_file.write("ROBINHOOD ID\n")
    securities_file.write("</UNIQUEIDTYPE>\n")
    securities_file.write("</SECID>\n")
    securities_file.write("<SECNAME>\n")
    securities_file.write(instrument_name + "\n")
    securities_file.write("</SECNAME>\n")
    securities_file.write("<TICKER>\n")
    securities_file.write(instrument_symbol + "\n")
    securities_file.write("</TICKER>\n")
    securities_file.write("</SECINFO>\n")
    securities_file.write("<STOCKTYPE>\n")
    securities_file.write("COMMON\n")
    securities_file.write("<STOCKTYPE>\n")   
    securities_file.write("</STOCKINFO>\n")
    
securities_file.write("</SECLIST>\n")
securities_file.write("</SECLISTMSGSRSV1>\n")
securities_file.write("</OFX>\n")


#Program termination
transaction_file.close()
securities_file.close()
requests.get("https://api.robinhood.com/logout/", headers = header)
