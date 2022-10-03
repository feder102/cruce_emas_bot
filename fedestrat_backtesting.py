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
        df = pd.DataFrame(client.get_historical_klines(symbol,interval, "1 May, 2022"))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol,interval, "1 May, 2022"))
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df

def tradingstrat(symbol, interval, qty, open_position = False, busco_long=True):
    df = getData(symbol, interval)    
    i=202
    busco_long = busco_long
    while i <= len(df):
        #print(f'precio del {symbol} = {(df.Close.iloc[i-1])}')
        #Compramos cuando macd_diff (La diferencia entre macdd y signal)
        #https://github.com/bukosabino/ta
        #https://medium.com/datos-y-ciencia/biblioteca-de-an%C3%A1lisis-t%C3%A9cnico-sobre-series-temporales-financieras-para-machine-learning-con-cb28f9427d0
        if not open_position and i <= len(df): #LONG
            cant_profit = 0
            cant_stop   = 0
            if busco_long:
                if  ema_indicator(df.Close,window=50).iloc[i-1] > ema_indicator(df.Close,window=200).iloc[i-1] \
                    and ema_indicator(df.Close,window=50).iloc[i-2] < ema_indicator(df.Close,window=200).iloc[i-2] \
                    and i <= len(df):
                    time = df.index.values[i-1]
                    #sleep(150)#Espero 2.5 minutos para que el precio corra
                    while True and i <= len(df):
                        #La distancia que tiene el precio de la ema de 200 es +/- 6%
                        #distancia_mayor tiene el precio maximo que puede alcanzar la distanciade la ema
                        #distancia_menor tiene el precio minimo que puede alcanzar la distanciade la ema
                        last_ema_200 = float(ema_indicator(df.Close,window=200).iloc[i-1])
                        distancia_mayor = last_ema_200 + ((last_ema_200 * 0.2) / 100)
                        distancia_menor = last_ema_200 - ((last_ema_200 * 0.2) / 100)
                        #SI el precio esta entre estas distancias quiere decir que hizo el pullback
                        #Entonces voy log
                        if df.Close.iloc[i-1] <= distancia_mayor and df.Close.iloc[i-1] >= distancia_menor:
                            #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)
                            open_position = True
                            #buyprice = float(order['fills'][0]['price'])
                            buyprice = float(df.Close.iloc[i-1])
                            cantPrice = float(buyprice * qty)
                            profit = float(df.Close.iloc[i-1]) * 1.06
                            stop = float(df.Close.iloc[i-1]) * 0.94
                            time = df.index.values[i-1]
                            message  = 'Simbolo ' + str(symbol) \
                                + '\nFecha:  ' + str(time) \
                                + '\nPrecioActual:  ' + str(buyprice) \
                                + '\nPrecioProfitDeseado:  ' + str(profit) \
                                + '\nPrecioStopDeseado:  ' + str(stop) \
                                + '\nOperacion :  ' + 'BUY'
                            sleep(5)
                            bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                            break
                        i = i + 1
            else:
                #SHORT
                if ema_indicator(df.Close,window=50).iloc[i-1] < ema_indicator(df.Close,window=200).iloc[i-1] \
                    and ema_indicator(df.Close,window=50).iloc[i-2] > ema_indicator(df.Close,window=200).iloc[i-2] \
                    and i <= len(df):
                    time = df.index.values[i-1]
                    while True and i <= len(df):
                        #La distancia que tiene el precio de la ema de 200 es +/- 6%
                        #distancia_mayor tiene el precio maximo que puede alcanzar la distanciade la ema
                        #distancia_menor tiene el precio minimo que puede alcanzar la distanciade la ema
                        last_ema_200 = float(ema_indicator(df.Close,window=200).iloc[i-1])
                        distancia_mayor = last_ema_200 + ((last_ema_200 * 0.2) / 100)
                        distancia_menor = last_ema_200 - ((last_ema_200 * 0.2) / 100)
                        #SI el precio esta entre estas distancias quiere decir que hizo el pullback
                        #Entonces voy log
                        if df.Close.iloc[i-1] <= distancia_mayor and df.Close.iloc[i-1] >= distancia_menor:
                            #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)
                            open_position = True
                            #buyprice = float(order['fills'][0]['price'])
                            buyprice = float(df.Close.iloc[i-1])
                            cantPrice = float(buyprice * qty)
                            profit = float(df.Close.iloc[i-1]) * 0.94
                            stop = float(df.Close.iloc[i-1]) * 1.06
                            time = df.index.values[i-1]
                            message  = 'Simbolo ' + str(symbol) \
                                + '\nFecha:  ' + str(time) \
                                + '\nPrecioActual:  ' + str(buyprice) \
                                + '\nPrecioProfitDeseado:  ' + str(profit) \
                                + '\nPrecioStopDeseado:  ' + str(stop) \
                                + '\nOperacion :  ' + 'SHORT'
                            sleep(5)
                            bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                            break
                        i = i + 1
            
        #sleep(60)
        if open_position and i <= len(df):
            while True and i <= len(df):

                if busco_long:
                    if  df.Close.iloc[i-1] >= profit and i <= len(df):
                        #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                        #sellprice = float(order['fills'][0]['price'])
                        sellprice = float(df.Close.iloc[i-1])
                        time = df.index.values[i-1]
                        print(f'profit = {(sellprice - cantPrice)}')
                        open_position = False
                        message  = 'Simbolo ' + str(symbol) \
                            + '\nPrecioActual:  ' + str(df.Close.iloc[i-1]) \
                            + '\nFecha:  ' + str(time) \
                            + '\nOperacion :  ' + 'PROFIT' \
                            + '\nProfit :' + str((sellprice - cantPrice))
                        sleep(5)
                        cant_profit = cant_profit + 1
                        bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                        break
                    if  df.Close.iloc[i-1] <= stop and i <= len(df):
                        #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                        #sellprice = float(order['fills'][0]['price'])                       
                        sellprice = float(df.Close.iloc[i-1])
                        print(f'perdido = {(cantPrice - sellprice)}')
                        time = df.index.values[i-1]
                        open_position = False
                        message  = 'Simbolo ' + str(symbol) \
                            + '\nPrecioActual:  ' + str(df.Close.iloc[i-1]) \
                            + '\nFecha:  ' + str(time) \
                            + '\nOperacion :  ' + 'STOP' \
                            + '\nStopLoss :' + str((cantPrice / sellprice) - qty)
                        sleep(5)
                        cant_stop = cant_stop + 1
                        bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                        break
                    i = i + 1
                else:#SHORT
                    if  df.Close.iloc[i-1] <= profit and i <= len(df):
                        #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                        #sellprice = float(order['fills'][0]['price'])
                        sellprice = float(df.Close.iloc[i-1])
                        time = df.index.values[i-1]
                        print(f'profit = {(cantPrice / sellprice) - qty}')
                        open_position = False
                        message  = 'Simbolo ' + str(symbol) \
                            + '\nPrecioActual:  ' + str(df.Close.iloc[i-1]) \
                            + '\nFecha:  ' + str(time) \
                            + '\nOperacion :  ' + 'PROFIT' \
                            + '\nProfit :' + str((cantPrice / sellprice) - qty)
                        sleep(5)
                        cant_profit = cant_profit + 1
                        bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                        break
                    if  df.Close.iloc[i-1] >= stop and i <= len(df):
                        #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                        #sellprice = float(order['fills'][0]['price'])
                        sellprice = float(df.Close.iloc[i-1])
                        print(f'perdido = {qty - (sellprice / cantPrice)}')
                        time = df.index.values[i-1]
                        open_position = False
                        message  = 'Simbolo ' + str(symbol) \
                            + '\nPrecioActual:  ' + str(df.Close.iloc[i-1]) \
                            + '\nFecha:  ' + str(time) \
                            + '\nOperacion :  ' + 'STOP' \
                            + '\nStopLoss :' + str(qty - (sellprice / cantPrice))
                        sleep(5)
                        cant_stop = cant_stop + 1
                        bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                        break
                    i = i + 1
        i= i + 1
    message  = 'Simbolo ' + str(symbol) \
                        + '\nCANTIDAD PROFIT:  ' + str(cant_profit) \
                        + '\nCANTIDAD STOPLOSS:  ' + str(cant_stop) 
    sleep(5)        
    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
    print(f'Ope. Ganados = {cant_profit}')
    print(f'Ope. Perdidas = {cant_stop}')