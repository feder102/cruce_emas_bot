
# La estrategia consiste en 
# 1) Espero que la ema de 50 cruce la ema de 200
# 2) Si la ema de 50 cruzo para abajo la ema de 200, espero el pullback a la ema de 200, 
#    margen de cercania a la ema de 200 es del 0.6%
# 3) Abro una operacion Short con un profit del 6% y un stoploss del 6%

# Usaré una orden de venta OCO como ejemplo en BTCUSDT.
# Imagina que tengo 1 BTC. El precio actual es de 30157,85 y quiero vender 1 BTC mucho más alto a 32000,07
# Pero el precio no sube y comienza a bajar, entonces coloco mi stopPrice en 29283.03 donde se abrirá la orden de venta limitada al precio 29000.00
# Esto significa que venderé a 32000.07 o 29000.00 USDT. La orden está escrita de la siguiente manera
# order= client.order_oco_sell(
#     symbol= 'BTCUSDT',                                            
#     quantity= 1.00000,                                            
#     price= '32000.07',                                            
#     stopPrice= '29283.03',                                            
#     stopLimitPrice= '29000.00',                                            
#     stopLimitTimeInForce= 'FOK')


# info = client.get_symbol_info(symbol)
#         step_size = info['filters'][2]['stepSize']
#         minNotonial = float(info['filters'][3]['minNotional'])+1
#         infoa = client.get_account()
#         bal= infoa['balances']
#         i_o = float(bal[188]['free'])
        
#         buyprice = float(df.Close.iloc[-1]) * 0.98
#         profit = float(df.Close.iloc[-1]) * 1.06
#         stop = float(df.Close.iloc[-1]) * 0.94
#         qty = minNotonial/float(stop)
#         time = df.index.values[len(df)-1]

#         qty =  format_value(qty, step_size)
#         price =  format_value(buyprice, step_size)

#         order = client.order_limit_buy(
#                     symbol    = symbol,
#                     quantity  = qty,
#                     price     = price
#                 )
#         print(order)


# TEST
# ocoOrder= client.create_test_order(
#     symbol='BTCUSDT',
#     side=SIDE_SELL,
#     type=ORDER_TYPE_OCO,
#     timeInForce=TIME_IN_FORCE_GTC,
#     quantity=0.002,
#     stopPrice='7000',
#     stopLimitPrice='7500',
#     price='11000')


from time import sleep
from binance.client import Client
from numpy import signedinteger
import pandas as pd
from ta.trend import ema_indicator
import config
import telegram
import binance.exceptions as BinanceAPIException

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
def getData(symbol,interval):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=205))
    except BinanceAPIException as e:
        if e.code==-2013:
            print ("Order does not exist.")
        elif e.code==-2014:
            print ("API-key format invalid.")
        print ("This is an error message!{}".format(e))
        #End If
        sleep(30)
        df = pd.DataFrame(client.get_historical_klines(symbol,interval,limit=205))
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df

#Calcula el tamaño para la compra, la presicion del precio para que no de error de filtro
def step_size_to_precision(ss):
    return ss.find('1') - 1


def format_value(val, step_size_str):
    precision = step_size_to_precision(step_size_str)
    return "{:0.0{}f}".format(val, precision)

def tradingstrat(symbol, interval, open_position = False, busco_long = True):
    while True:
        sleep(3)
        df = getData(symbol, interval)
        busco_long = busco_long
        qty=0
        print(f'precio del {symbol} = {(df.Close.iloc[-1])}')
        #https://github.com/bukosabino/ta
        #https://medium.com/datos-y-ciencia/biblioteca-de-an%C3%A1lisis-t%C3%A9cnico-sobre-series-temporales-financieras-para-machine-learning-con-cb28f9427d0
        #PONER ORDENES OCO con profit y stop loss
        if not open_position: #LONG
            if busco_long:
                pasa = True
                if pasa:
                # if  ema_indicator(df.Close,window=50).iloc[-1] > ema_indicator(df.Close,window=200).iloc[-1] \
                #     and ema_indicator(df.Close,window=50).iloc[-2] < ema_indicator(df.Close,window=200).iloc[-2]:
                #     sleep(30)
                    while True:
                        #Espero para que el precio corra
                        #La distancia que tiene el precio de la ema de 200 es +/- 6%
                        #distancia_mayor tiene el precio maximo que puede alcanzar la distanciade la ema
                        #distancia_menor tiene el precio minimo que puede alcanzar la distanciade la ema
                        print("Estoy esperando el pullback para ir long...")
                        print(f'precio del {symbol} = {(df.Close.iloc[-1])}')
                        last_ema_200 = float(ema_indicator(df.Close,window=200).iloc[-1])
                        distancia_mayor = last_ema_200 + ((last_ema_200 * 0.3) / 100)
                        distancia_menor = last_ema_200 - ((last_ema_200 * 0.3) / 100)
                        #SI el precio esta entre estas distancias quiere decir que hizo el pullback
                        #Entonces voy log
                        if df.Close.iloc[-1] <= distancia_mayor and df.Close.iloc[-1] >= distancia_menor:
                            #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)                           
                            open_position = True
                             # BEGIN GET PRICE
                            try:
                                client = Client(config.API_KEY, config.API_SECRET, tld='com')
                                info = client.get_symbol_info(symbol)
                                step_size = info['filters'][2]['stepSize']
                                #Min Notonial es lo minimo en dolar que puedo compra ejemplo 10usd
                                minNotonial = float(info['filters'][3]['minNotional']) + 1
                                infoa = client.get_account()
                                bal   = infoa['balances']
                                #Balance en BUSD [188]
                                usd = float(bal[188]['free'])
                                if (usd > minNotonial):
                                    buyprice = float(df.Close.iloc[-1]) * 0.995
                                    profit = float(df.Close.iloc[-1]) * 1.02
                                    stop = float(df.Close.iloc[-1]) * 0.98
                                    limit = float(df.Close.iloc[-1]) * 0.99
                                    qty = minNotonial/float(stop)
                                    time = df.index.values[len(df)-1]

                                    qty   =  format_value(qty, step_size)
                                    price =  format_value(buyprice, step_size)
                                    stop  =  format_value(stop, step_size)
                                    limit  =  format_value(limit, step_size)

                                    order = client.create_order(
                                                symbol    = symbol,
                                                side    = client.SIDE_BUY,
                                                type = client.ORDER_TYPE_LIMIT,
                                                quantity  = qty,
                                                price     = price,
                                                timeInForce = client.TIME_IN_FORCE_GTC
                                            )
                                    print(order)

                                    sleep(10)

                                    message  = 'Simbolo ' + str(symbol) \
                                        + '\nFecha:  ' + str(time) \
                                        + '\nPrecioActual:  ' + str(buyprice) \
                                        + '\nPrecioProfitDeseado:  ' + str(profit) \
                                        + '\nPrecioStopDeseado:  ' + str(stop) \
                                        + '\nPrecioStopLimitDeseado:  ' + str(limit) \
                                        + '\nOperacion :  ' + 'BUY'
                                    sleep(5)
                                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                                else:
                                    message  = 'Simbolo ' + str(symbol) \
                                        + '\nFecha:  ' + str(time) \
                                        + '\nMensaje:  ' + 'Me quede sin saldo'
                                    sleep(5)
                                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                            except Exception as e:
                                time = df.index.values[len(df)-1]
                                with open("errores/Errores_en_{symbol}_{time}.txt", "a") as myfile:
                                    myfile.write(str(time) +" - an exception occured - {}".format(e)+ " Oops 1 ! \n")
                                client = Client(config.API_KEY, config.API_SECRET, tld='com')
                                orders = client.get_open_orders(symbol=symbol)
                                if (len(orders)>0):
                                    i = 0
                                    while(i<len(orders)):
                                        result = client.cancel_order(
                                        symbol=symbol,
                                        orderId=orders[i].get('orderId'))
                                        i = i +1
                                        print(result)
                                continue
                            break
                        else:
                            sleep(3)
                            df = getData(symbol, interval)
                    break
            else:#SHORT
                if  ema_indicator(df.Close,window=50).iloc[-1] < ema_indicator(df.Close,window=200).iloc[-1] \
                    and ema_indicator(df.Close,window=50).iloc[-2] > ema_indicator(df.Close,window=200).iloc[-2]:

                    sleep(50)#Espero 2.5 minutos para que el precio corra
                    while True:
                        #La distancia que tiene el precio de la ema de 200 es +/- 6%
                        #distancia_mayor tiene el precio maximo que puede alcanzar la distanciade la ema
                        #distancia_menor tiene el precio minimo que puede alcanzar la distanciade la ema
                        print("Estoy esperando el pullback para ir short...")
                        last_ema_200 = float(ema_indicator(df.Close,window=200).iloc[-1])
                        distancia_mayor = last_ema_200 + ((last_ema_200 * 0.2) / 100)
                        distancia_menor = last_ema_200 - ((last_ema_200 * 0.2) / 100)
                        #SI el precio esta entre estas distancias quiere decir que hizo el pullback
                        #Entonces voy log
                        if df.Close.iloc[-1] <= distancia_mayor and df.Close.iloc[-1] >= distancia_menor:
                            #order = client.create_order(symbol= symbol, side='BUY', type = 'MARKET', quantity=qty)
                            
                            open_position = True
                            #buyprice = float(order['fills'][0]['price'])
                            buyprice = float(df.Close.iloc[-1])
                            cantPrice = float(buyprice * qty)
                            profit = float(df.Close.iloc[-1]) * 0.94
                            stop = float(df.Close.iloc[-1]) * 1.06
                            time = df.index.values[len(df)-1]
                            order = client.order_oco_sell(
                                    symbol= symbol,                                            
                                    quantity= qty,                                            
                                    price= '{:.4f}'.format(round(profit,4)),                                            
                                    stopPrice= '{:.4f}'.format(round(stop * 1.002,4)),                                            
                                    stopLimitPrice= '{:.4f}'.format(round(stop ,4)),                                            
                                    stopLimitTimeInForce= 'FOK')
                            print(order)
                            message  = 'Simbolo ' + str(symbol) \
                                + '\nFecha:  ' + str(time) \
                                + '\nPrecioActual:  ' + str(buyprice) \
                                + '\nPrecioProfitDeseado:  ' + str(profit) \
                                + '\nPrecioStopDeseado:  ' + str(stop) \
                                + '\nOperacion :  ' + 'SHORT'
                            bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                            break
                        else:
                            sleep(3)
                            df = getData(symbol, interval)
                    break
        else: break         

    sleep(50)
    if open_position:
        while True:
            sleep(3)
            df = getData(symbol, interval)
            if busco_long:
                if  df.Close.iloc[-1] >= profit:
                    #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                    #sellprice = float(order['fills'][0]['price'])
                    sellprice = float(df.Close.iloc[-1])
                    time = df.index.values[len(df)-1]
                    print(f'profit = {(sellprice - cantPrice)}')
                    open_position = False

                    price =  format_value(sellprice, step_size)

                    order = client.create_order(
                                symbol    = symbol,
                                side    = client.SIDE_SELL,
                                type = client.ORDER_TYPE_LIMIT,
                                quantity  = qty,
                                price     = profit,
                                timeInForce = client.TIME_IN_FORCE_GTC
                            )
                    print(order)

                    message  = 'Simbolo ' + str(symbol) \
                        + '\nPrecioActual:  ' + str(buyprice) \
                        + '\nFecha:  ' + str(time) \
                        + '\nOperacion :  ' + 'PROFIT' \
                        + '\nProfit :' + str((sellprice - cantPrice))
                    sleep(5)
                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                    break
                if  df.Close.iloc[-1] <= float(stop):
                    #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                    #sellprice = float(order['fills'][0]['price'])
                    sellprice = float(df.Close.iloc[-1])
                    time = df.index.values[len(df)-1]
                    print(f'perdido = {(cantPrice - sellprice)}')
                    open_position = False

                    order = client.create_order(
                                symbol    = symbol,
                                side    = client.SIDE_SELL,
                                type = client.ORDER_TYPE_MARKET,
                                quantity  = qty,
                                price     = stop,
                                timeInForce = client.TIME_IN_FORCE_GTC
                            )
                    print(order)

                    message  = 'Simbolo ' + str(symbol) \
                        + '\nPrecioActual:  ' + str(buyprice) \
                        + '\nFecha:  ' + str(time) \
                        + '\nOperacion :  ' + 'STOP' \
                        + '\nStopLoss :' + str((cantPrice - sellprice))
                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                    break
            else:#SHORT
                if  df.Close.iloc[-1] <= profit:
                    #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                    #sellprice = float(order['fills'][0]['price'])
                    sellprice = float(df.Close.iloc[-1])
                    time = df.index.values[len(df)-1]
                    print(f'profit = {(cantPrice / sellprice) - qty}')
                    open_position = False
                    message  = 'Simbolo ' + str(symbol) \
                        + '\nPrecioActual:  ' + str(df.Close.iloc[-1]) \
                        + '\nFecha:  ' + str(time) \
                        + '\nOperacion :  ' + 'PROFIT' \
                        + '\nProfit :' + str((cantPrice / sellprice) - qty)
                    sleep(5)
                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                    break
                if  df.Close.iloc[-1] >= stop:
                    #order = client.create_order(symbol= symbol, side='SELL', type = 'MARKET', quantity=qty)
                    #sellprice = float(order['fills'][0]['price'])
                    sellprice = float(df.Close.iloc[-1])
                    time = df.index.values[len(df)-1]
                    print(f'profit = {qty - (sellprice / cantPrice)}')
                    open_position = False
                    message  = 'Simbolo ' + str(symbol) \
                        + '\nPrecioActual:  ' + str(df.Close.iloc[-1]) \
                        + '\nFecha:  ' + str(time) \
                        + '\nOperacion :  ' + 'STOP' \
                        + '\nStopLoss :' + str(qty - (sellprice / cantPrice))
                    sleep(5)
                    bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                    break