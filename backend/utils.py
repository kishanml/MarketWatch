import pandas as pd
import numpy as np
import datetime as dt
import json
import subprocess
from typing  import List, Dict
import os

DATETIME_FORMAT = "%d:%m:%Y %H:%M"


def get_instrument_tokens(instruments: list, current_price: float, top_k: int):

    current_datetime = dt.datetime.now()

    current_date = current_datetime.strftime('%d:%m:%Y')
    is_current_month_data_present = any([ file.startswith(current_date+'_option') for file in os.listdir('./')])
    filename = f"{current_date}_option_strike_instruments.csv"

    if not is_current_month_data_present:
        subprocess.run([
            'curl', '-o', filename,

            "https://api.kite.trade/instruments",
            "-H", "X-Kite-Version: 3",
            "-H", "Authorization: token api_key:access_token"
        ])

    df = pd.read_csv(filename)
    df = df.dropna(subset=['expiry'], axis=0)
    instrument_types = ['CE', 'PE']
    df['expiry'] = pd.to_datetime(df['expiry'], errors='coerce')

    df = df.loc[df['expiry'].dt.month == current_datetime.month]

    df['expiry_day'] = df['expiry'].apply(lambda x: x.strftime('%b').upper())
    df['expiry_day_diff'] = (df['expiry'] - dt.datetime.now())
    df['expiry_day_diff'] = df['expiry_day_diff'].apply(
        lambda x: np.round(x.total_seconds()/86400, 3))

    df['strikes_diff'] = df['strike'].apply(lambda x: x-current_price)

    # data = df.loc[((df['name'].isin(instruments)) & (df['segment'] == 'MCX-OPT') & (df['instrument_type'].isin(instrument_types)) & (df['expiry_day_diff'] > 0)
    #                & (df['expiry_day_diff'] <= 50)), ["instrument_token", "tradingsymbol", "expiry", "strike", "instrument_type", "name", "expiry_day_diff", "strikes_diff"]]

    data=df.loc[((df['name'].isin(instruments)) & (df['segment']=='NFO-OPT') & (df['instrument_type'].isin(instrument_types)) & (df['expiry_day_diff']>0)&(df['expiry_day_diff']<=30) ),["instrument_token","tradingsymbol","expiry","strike","instrument_type","name","expiry_day_diff","strikes_diff"]]
    ce_data = data.loc[data['instrument_type']=='CE'].sort_values(by=['strikes_diff', 'expiry_day_diff'], ascending=[True, True]).head(top_k)
    pe_data = data.loc[data['instrument_type']=='PE'].sort_values(by=['strikes_diff', 'expiry_day_diff'], ascending=[True, True]).head(top_k)

    data = pd.concat([ce_data,pe_data],axis=0,ignore_index=True).reset_index(drop=True)
    print(data)
    return data.reset_index(drop=True).to_dict('records')



class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dt.datetime):
            return obj.strftime("%d/%m/%Y %H:%M:%S")
        elif isinstance(obj, dt.timedelta):
            return str(obj)
        else:
            return super().default(obj)
                       