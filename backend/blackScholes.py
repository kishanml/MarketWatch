import pandas as pd
import re
import json
import datetime, calendar
from constants import *
import mibian



zerodha_weekly_month_mapper = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": "O", "NOV": "N", "DEC": "D"}
rev_month_mapper = {v:k for k,v in zerodha_weekly_month_mapper.items()}


def LastThursdayInMonth(year, month):
    daysInMonth = calendar.monthrange(year, month)[1]   
    dt = datetime.date(year, month, daysInMonth)

    offset = 4 - dt.isoweekday()
    if offset > 0: offset -= 7                         
    dt += datetime.timedelta(offset)                  

    now = datetime.date.today()                       
    if dt.year == now.year and dt.month == now.month and dt < now:
        raise Exception('Oops - missed the last Thursday of this month')

    return dt


def get_iv_gamma(ltp,strike,risk_free_rate,exp_diff,opt_price,opt_type='CE'):
    if opt_type=="CE":
        iv = mibian.BS([ltp, strike,risk_free_rate, exp_diff], callPrice=opt_price).impliedVolatility
        mb_call = mibian.BS([ltp, strike,risk_free_rate, exp_diff],volatility=iv)
        exp_price = mb_call.callPrice
        delta = mb_call.callDelta
        theta = mb_call.callTheta
        rho = mb_call.callRho
        gamma = mb_call.gamma
        vega = mb_call.vega

    elif opt_type=="PE":
        iv = mibian.BS([ltp, strike,risk_free_rate, exp_diff], putPrice=opt_price).impliedVolatility
        mb_put = mibian.BS([ltp, strike,risk_free_rate, exp_diff],volatility=iv)
        exp_price = mb_put.putPrice
        delta = mb_put.putDelta
        theta = mb_put.putTheta
        rho = mb_put.putRho
        gamma = mb_put.gamma
        vega = mb_put.vega


    return iv,gamma,exp_price
        

def get_strike_and_expiry(strike_str,current_month_str):

    regex_1 = "\d{2}%s\d{2}"%zerodha_weekly_month_mapper[current_month_str]
    regex_2 = "\d{2}%s"%current_month_str
    flag_1= re.search(regex_1,strike_str)
    flag_2 = re.search(regex_2,strike_str)
    
    if flag_1 is not None:
        # weekly expiry
        span_1 = flag_1.span()
        expiry_str = strike_str[span_1[0]:span_1[1]]
        expiry_str=expiry_str.replace(zerodha_weekly_month_mapper[current_month_str],rev_month_mapper[zerodha_weekly_month_mapper[current_month_str]])
        expiry_date = pd.to_datetime(expiry_str,format='%y%b%d').strftime('%d/%m/%Y')
        strikePrice = eval(strike_str[span_1[1]:-2])

        return expiry_date,strikePrice

    elif flag_2 is not None:

        span_2 = flag_2.span()
        expiry_str = strike_str[span_2[0]:span_2[1]]
        ref_object = pd.to_datetime(expiry_str,format='%y%b')
        expiry_date = pd.to_datetime(LastThursdayInMonth(ref_object.year,ref_object.month)).strftime('%d/%m/%Y')
        strikePrice = eval(strike_str[span_2[1]:-2])
        

        return expiry_date,strikePrice

def generate_iv_details(data):

    call_data = pd.DataFrame(data['call_data'])
    put_data = pd.DataFrame(data['put_data'])
    current_price = data['current_price']
    current_time = pd.to_datetime(data['last_datetime'],format="%d:%m:%Y %H:%M")
    current_month_alp = current_time.strftime('%b').upper()

    # generates for call option
    call_data[['expiry', 'strike']] = call_data.apply(lambda x: pd.Series(get_strike_and_expiry(x['trading_symbol'],current_month_alp)),axis=1)
    call_data['expiry'] = pd.to_datetime(call_data['expiry'],format="%d/%m/%Y")
    call_data['last_trade_time'] = pd.to_datetime(call_data['last_trade_time'],format="%d/%m/%Y %H:%M:%S")
    call_data['expiry_diff'] = call_data.apply(lambda x: (x['expiry'] - x['last_trade_time']).total_seconds() / 86400,  axis=1)
    call_data['expiry'] = call_data['expiry'].apply(lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else '')
    call_data['last_trade_time'] = call_data['last_trade_time'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(x) else '')
    call_data[['iv','gamma','exp_price']]= call_data.apply(lambda x : pd.Series(get_iv_gamma(current_price,x.strike,RISK_FREE_RATE,x.expiry_diff,x.last_traded_price,'CE')),axis=1)
    call_data['Gvalue'] = round(call_data['gamma']*current_price*call_data['oi'],3)   

    #generates for put option
    put_data[['expiry', 'strike']] = put_data.apply(lambda x: pd.Series(get_strike_and_expiry(x['trading_symbol'],current_month_alp)),axis=1)
    put_data['expiry'] = pd.to_datetime(put_data['expiry'],format="%d/%m/%Y")
    put_data['last_trade_time'] = pd.to_datetime(put_data['last_trade_time'],format="%d/%m/%Y %H:%M:%S")
    put_data['expiry_diff'] = put_data.apply(lambda x: (x['expiry'] - x['last_trade_time']).total_seconds() / 86400,  axis=1)
    put_data['expiry'] = put_data['expiry'].apply(lambda x: x.strftime("%d/%m/%Y") if pd.notna(x) else '')
    put_data['last_trade_time'] = put_data['last_trade_time'].apply(lambda x: x.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(x) else '')
    put_data[['iv','gamma','exp_price']]= put_data.apply(lambda x : pd.Series(get_iv_gamma(current_price,x.strike,RISK_FREE_RATE,x.expiry_diff,x.last_traded_price,'PE')),axis=1)
    put_data['Gvalue'] = round(put_data['gamma']*current_price*put_data['oi'],3)

    data["cpg_value"] = round(call_data['Gvalue'].sum() - put_data['Gvalue'].sum())
    # call_data= call_data[['trading_symbol','instrument_type','iv','oi','Gvalue']]
    # put_data = put_data[['trading_symbol','instrument_type','iv','oi','Gvalue']]
    call_data= call_data.fillna(0)
    put_data = put_data.fillna(0)
    data["call_data"]=call_data.to_dict('records')
    data["put_data"]=put_data.to_dict('records')

    return json.dumps(data)



