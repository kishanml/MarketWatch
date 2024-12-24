import os
import json
import uuid
import random
import pickle
import datetime as dt
import threading

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from kiteconnect import KiteTicker

from KiteFunc import LoginKite
from utils import get_instrument_tokens, DATETIME_FORMAT, JSONEncoder
from constants import *
from blackScholes import generate_iv_details

import pandas as pd
import numpy as np

load_dotenv()



os.makedirs('save_data',exist_ok=True)
# App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")

kws = None
instrument_tokens = []
instrument_last_price= None
instrument_token_2_symbol_mapper = None
current_orders_dataframe = pd.DataFrame()
prev_orders_dataframe = pd.DataFrame()
next_min = None
kite_obj=None
input_instruments= None
price_change = None 
prev_instrument_last_price = -1
last_datetime =None



thread_lock = Lock()


def get_instrument_details(input_instruments):

    global kite_obj
    mapper = {'NIFTY':'NIFTY 50','BANKNIFTY':'NIFTY BANK'}
    apply_mapper = lambda x : f'NSE:{mapper.get(x,x)}'
    instruments = list(map(apply_mapper,input_instruments))
    instrument_details = kite_obj.ltp(instruments)[instruments[0]]
    # print(instrument_details)

    # instrument_details = {"GOLD":{'last_price':76500}}
    # instrument_details = instrument_details[input_instruments[0]]

    return instrument_details




def process_stock_orders(ticks):
    global instrument_token_2_symbol_mapper,current_orders_dataframe
    output =[]
    # print(instrument_token_2_symbol_mapper)
    for ele in ticks:
        if ele['volume_traded']>0 and instrument_token_2_symbol_mapper.get(ele['instrument_token'],None):
            output.append(
                {
                "trading_symbol": instrument_token_2_symbol_mapper[ele['instrument_token']][0],
                "instrument_type" : instrument_token_2_symbol_mapper[ele['instrument_token']][1],
                "last_traded_price": ele['last_price'],
                "last_trade_time" : ele['last_trade_time'],
                "volume_traded" : ele['volume_traded'],
                "oi" : ele['oi'],
                "oi_change": 0
                
            })

    current_orders_dataframe = pd.concat([current_orders_dataframe,pd.DataFrame(output)])



# Callback for successful connection
def on_connect(ws, response):
    print("Connected successfully. Response:", response)
    ws.subscribe(instrument_tokens)
    ws.set_mode(ws.MODE_FULL, instrument_tokens)
    print(f"Subscribed to tokens in Full mode: {instrument_tokens}")

# Callback for connection closure
def on_close(ws, code, reason):
    print(f"Connection closed: {code} - {reason}")

# Callback for connection errors
def on_error(ws, code, reason):
    print(f"Connection error: {code} - {reason}")

# Callback for reconnection attempts
def on_reconnect(ws, attempts_count):
    print(f"Reconnecting: Attempt {attempts_count}")

# Callback when reconnection fails
def on_noreconnect(ws):
    print("Reconnection failed.")

# Callback for receiving tick data
def on_ticks(ws, ticks):
    global next_min,current_orders_dataframe,prev_orders_dataframe,input_instruments,instrument_last_price,price_change,prev_instrument_last_price,last_datetime
    current_time = dt.datetime.now()

    if len(ticks)>0:
        print(len(ticks))
        # Emit data every 5 minutes
        print('is',current_time.minute%2)
        if current_time.minute%2 ==0:  
            next_min = current_time.minute+1
            # print('here',next_min)
            # print(str(ticks))
            process_stock_orders(ticks)
            instrument_last_price = get_instrument_details(input_instruments)['last_price']
            last_datetime = current_time.strftime(DATETIME_FORMAT)
    
            # if accumulated_ticks:
        print(current_time.minute,next_min)
        if current_time.minute==next_min:
            print('here2')
           
            if current_orders_dataframe.shape[0]:

                grouped_orders = current_orders_dataframe.groupby(by=['trading_symbol','instrument_type']).agg({
                "last_traded_price": 'last',
                "last_trade_time" : 'last',
                "volume_traded" : 'last',
                "oi" :'last',
                "oi_change": 'last'}).reset_index()
                print('grouped',grouped_orders)

                print('pre',prev_orders_dataframe)
                if prev_orders_dataframe.shape[0] and prev_instrument_last_price>0:
                    
                    merged_df = pd.merge(grouped_orders, prev_orders_dataframe, on=['trading_symbol','instrument_type'], how='outer', suffixes=('_current', '_previous'))
                    merged_df['oi_change'] = merged_df['oi_current'] - merged_df['oi_previous']
                    merged_df = merged_df.dropna(subset=['oi_current'])
                    merged_df= merged_df.fillna(0)
                    # {"trading_symbol": "SILVERM24NOVFUT", "instrument_type": "PE", "last_asset_price_current": 94455, "last_traded_price_current": 94325.0, "last_trade_time_current": "05/11/2024 18:12:50", "volume_traded_current": 11846, "oi_current": 32725, "oi_change_current": 0, "last_asset_price_previous": 94455, "last_traded_price_previous": 94324.0, "last_trade_time_previous": "05/11/2024 18:10:52", "volume_traded_previous": 11778, "oi_previous": 32710, "oi_change_previous": 0, "oi_change": 15}
                    merged_df = merged_df.drop(columns=['oi_change_current','last_traded_price_previous','last_trade_time_previous','oi_previous','oi_change_previous','volume_traded_previous'])
                    merged_df = merged_df.rename(columns={ col : col.replace('_current',"") for col in merged_df.columns if col.endswith('_current')})
                    current_orders_dataframe = merged_df.reset_index(drop=True)
                    
                    price_change = round(prev_instrument_last_price-instrument_last_price,2)
                
                else:
                    current_orders_dataframe = grouped_orders
                    price_change= 0

                prev_orders_dataframe = current_orders_dataframe
                prev_instrument_last_price = instrument_last_price
                
                call_option_data = current_orders_dataframe.loc[current_orders_dataframe['instrument_type']=='CE'].reset_index(drop=True).to_dict('records')
                put_option_data = current_orders_dataframe.loc[current_orders_dataframe['instrument_type']=='PE'].reset_index(drop=True).to_dict('records')
                

                data  = json.loads(json.dumps({"call_data":call_option_data,
                                                    "put_data":put_option_data,
                                                    "current_price":instrument_last_price,
                                                    "price_change":price_change,
                                                    "last_datetime":last_datetime},cls=JSONEncoder) )
                
                print('genr')
                data=generate_iv_details(data)
                print('genr done')

                # json.dump(data,open(f'save_data/{uuid.uuid4()}.json','w'))

                # random_name = random.choice(os.listdir('save_data/'))
                # data = json.loads(open(os.path.join('save_data',random_name),'r'))

                socketio.emit('stock_data',data)


                next_min = None

@socketio.on('send_data')
def handle_send_data(finput):
    global instrument_tokens,instrument_token_2_symbol_mapper,instrument_last_price,kite_obj,input_instruments,current_orders_dataframe,prev_orders_dataframe,price_change,prev_instrument_last_price
    kite_obj = pickle.load(open('kite_obj.pkl','rb'))
    input_instruments = finput['instrumentNames']

    instrument_details = get_instrument_details(input_instruments)

    instrument_last_price = instrument_details['last_price']
    instrument_data = get_instrument_tokens(input_instruments,instrument_last_price,10)
    instrument_token_2_symbol_mapper = {ins['instrument_token'] : [ins['tradingsymbol'],ins['instrument_type']] for ins in instrument_data}
    print(instrument_token_2_symbol_mapper)
    # print(f"Received stock request for tokens: {instrument_tokens}")
    # instrument_token_2_symbol_mapper  = {109853703: ['SILVERMIC24NOVFUT','CE'],109134599:["SILVERM24NOVFUT","PE"]}
    if kws:
        kws.unsubscribe(instrument_tokens)  # Unsubscribe old tokens
    
    instrument_tokens= list(instrument_token_2_symbol_mapper.keys())
    # instrument_tokens = [109853703]
    current_orders_dataframe = pd.DataFrame()
    prev_orders_dataframe = pd.DataFrame()
    instrument_last_price= None
    price_change = None 
    prev_instrument_last_price = -1
    if kws:
        on_connect(kws, None)  # Resubscribe to the new tokens



def start_kite_ticker():
    global kws
    login_details = json.load(open('kite_details.json', 'r'))
    kws = KiteTicker(os.getenv('API_KEY'), login_details['access_token'])

    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.on_error = on_error
    kws.on_reconnect = on_reconnect
    kws.on_noreconnect = on_noreconnect
    kws.on_ticks = on_ticks

    kws.connect()

threading.Thread(target=start_kite_ticker).start()


class Login(Resource):
    def get(self):
        kite_obj ,login_details =  LoginKite().generate_kite_session()
        pickle.dump(kite_obj,open('kite_obj.pkl','wb'))
        print(login_details)
        # login_details = {
        #             "success":True,
        #             "request_token": "",
        #             "user_type": "",
        #             "email": "",
        #             "user_name": "",
        #             "user_id": "",
        #             "api_key": "",
        #             "access_token": "",
        #             "public_token": "",
        #             "meta": { "demat_consent": "physical" }
        #             }
        json.dump(login_details,open('kite_details.json','w'))

        return jsonify(login_details)

api.add_resource(Login, '/login')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

