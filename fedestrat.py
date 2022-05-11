'''
La estrategia consiste en 
1) Espero que la ema de 50 cruce la ema de 200
2) Si la ema de 50 cruzo para abajo la ema de 200, espero el pullback a la ema de 200, 
   margen de cercania a la ema de 200 es del 0.6%
3) Abro una operacion Short con un profit del 6% y un stoploss del 6%
'''

from time import sleep
from binance.client import Client
import pandas as pd
from ta.trend import ema_indicator
import config
import telegram
import binance.exceptions as BinanceAPIException

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
def getData(symbol,interval):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=200))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=200))
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
        if not open_position: #LONG
            if  ema_indicator(df.Close,window=50).iloc[-1] > ema_indicator(df.Close,window=200).iloc[-1] \
                and ema_indicator(df.Close,window=50).iloc[-2] < ema_indicator(df.Close,window=200).iloc[-2]:

                sleep(150)#Espero 2.5 minutos para que el precio corra
                while True:
                    #La distancia que tiene el precio de la ema de 200 es +/- 6%
                    #distancia_mayor tiene el precio maximo que puede alcanzar la distanciade la ema
                    #distancia_menor tiene el precio minimo que puede alcanzar la distanciade la ema
                    distancia_mayor = float(ema_indicator(df.Close,window=200).iloc[-1]) * 1.06
                    distancia_menor = float(ema_indicator(df.Close,window=200).iloc[-1]) * 0.94
                    #SI el precio esta entre estas distancias quiere decir que hizo el pullback
                    #Entonces voy log
                    if df.Close.iloc[-1] <= distancia_mayor and df.Close.iloc[-1] >= distancia_menor:
                        #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)
                        open_position = True
                        #buyprice = float(order['fills'][0]['price'])
                        buyprice = float(df.Close.iloc[-1])
                        profit = float(df.Close.iloc[-1]) * 1.06
                        stop = float(df.Close.iloc[-1]) * 0.94
                        time = df.index.values[len(df)-1]
                        message  = 'Simbolo ' + str(symbol) \
                            + '\nFecha:  ' + str(time) \
                            + '\nPrecioActual:  ' + str(buyprice) \
                            + '\nPrecioProfitDeseado:  ' + str(profit) \
                            + '\nPrecioStopDeseado:  ' + str(stop) \
                            + '\nOperacion :  ' + 'BUY'
                        bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                    break
                break
    sleep(60)
    if open_position:
        while True:
            df = getData(symbol, interval)

            if  df.Close.iloc[-1] >= profit:
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
            if  df.Close.iloc[-1] <= stop:
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
                    + '\nStopLoss :' + str((sellprice-buyprice)/buyprice)
                bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                break