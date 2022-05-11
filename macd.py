from time import sleep
from binance.client import Client
import pandas as pd
from ta.trend import macd_diff
import config
import telegram
import binance.exceptions as BinanceAPIException

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
def getData(symbol,interval):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=50))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=50))
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df

def tradingstrat(symbol, interval, qty, open_position = False):
    while True:
        df = getData(symbol, interval)
        print(f'precio del {symbol} = {(df.Close.iloc[-1])}')
        #Compramos cuando macd_diff (La diferencia entre macdd y signal)
        #https://github.com/bukosabino/ta
        #https://medium.com/datos-y-ciencia/biblioteca-de-an%C3%A1lisis-t%C3%A9cnico-sobre-series-temporales-financieras-para-machine-learning-con-cb28f9427d0
        if not open_position: 
            if  macd_diff(df.Close).iloc[-1] > 0 \
                and macd_diff(df.Close).iloc[-2] < 0:
                #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)
                open_position = True
                #buyprice = float(order['fills'][0]['price'])
                buyprice = float(df.Close.iloc[-1])
                time = df.index.values[len(df)-1]
                message  = 'Simbolo ' + str(symbol) \
                    + '\nFecha:  ' + str(time) \
                    + '\nPrecioActual:  ' + str(buyprice) \
                    + '\nOperacion :  ' + 'BUY'
                bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                break
    
    if open_position:
        while True:
            df = getData(symbol, interval)
            if  macd_diff(df.Close).iloc[-1] < 0 \
                and macd_diff(df.Close).iloc[-2] > 0:
                #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                #sellprice = float(order['fills'][0]['price'])
                sellprice = float(df.Close.iloc[-1])
                time = df.index.values[len(df)-1]
                print(f'profit = {(sellprice-buyprice)/buyprice}')
                open_position = False
                message  = 'Simbolo ' + str(symbol) \
                    + '\nPrecioActual:  ' + str(buyprice) \
                    + '\nFecha:  ' + str(time) \
                    + '\nOperacion :  ' + 'SELL' \
                    + '\nProfit :' + str((sellprice-buyprice)/buyprice)
                bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                break