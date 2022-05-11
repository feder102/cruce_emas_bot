import asyncio
import os
import config
import rsi_1
import telegram
import pandas as pd
import numpy as np 
from Csv_tool import csv_tool
from binance import AsyncClient, BinanceSocketManager,Client
from binance.exceptions import BinanceAPIException

#SEGUIR CON EL DINERO QUE LE MANDO QUE NO SE CREE EN LA CLASE RSI SINO ACA EN EL MAIN

async def main():
    bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client, user_timeout=60)
    interval = Client.KLINE_INTERVAL_5MINUTE
    # start any sockets here, i.e a trade socket    
    ts = bm.kline_socket('BTCUSDT',interval=interval)

    try:
        # then start receiving messages
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                klines=[]
                ganancias = 0
                comisiones = 0
                ganadoras = 0
                perdedoras = 0
                punto_ganadoras = []
                punto_perdedoras = []

                simbolo = res['k']['s']
                cs = csv_tool()
                path = 'csv/'+ simbolo + '_' + interval+'.csv'
                
                if(os.path.exists(path)):
                    if(res['k']['x'] == True):
                        cs.escribriCsv(res,True,path)
                        klines = cs.leerCsv(res)
                    else:
                        klines = cs.leerCsv(res)
                        df2 = pd.json_normalize(res['k'])
                        df2 = df2.assign(E=res['E'])        
                        df2 = df2.drop(['s','i','T','t','f','L','x','q','V','Q','V'], axis=1)
                        df2 = df2.reindex(columns=['E','o', 'c', 'h', 'l','v','n'])
                        df2 = df2.rename(columns={'E':'Date','o':'open','c':'close','h':'high','l':'low','v':'volume','n':'number_of_trade'})
                        df2 = df2.astype('float')
                        klines = pd.concat([klines, pd.DataFrame.from_records(df2)])
                else:
                    client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
                    klines = client.get_historical_klines(simbolo, interval, "1 Jan, 2022")
                    cs.escribriCsv(klines,False,path)
                    klines = cs.leerCsv(res)
                
                lineas_csv = cs.filasCsv(res)
                trade = rsi_1.Rsi_1(simbolo,klines,lineas_csv)
                ganancias = ganancias + trade.getGanancias()
                comisiones = comisiones + trade.getComisiones()

                ganadoras = ganadoras + trade.getCantProfit()
                perdedoras = perdedoras + trade.getCantStop()

                punto_ganadoras= np.append(punto_ganadoras,ganadoras)
                punto_perdedoras=np.append(punto_perdedoras,perdedoras)

                ganancias_plot= np.append(punto_ganadoras,ganadoras)
                
                
                message  = 'Simbolo ' + str(simbolo) + '\nGanancias: ' + str(trade.getGanancias()) \
                            + '\nComisiones:  ' + str(trade.getComisiones()) \
                            + '\nCantidad ganadas:  ' + str(trade.getCantProfit()) \
                            + '\nCantidad perdidas:  ' + str(trade.getCantStop()) \
                            + '\nNeto:  USD' + str(trade.getGanancias() - trade.getComisiones()) \
                            + '\nNeto:  ARS' + str((trade.getGanancias() - trade.getComisiones())*200) \
                            + '\nPrecioActual:  ' + str(res['k']['c'])
                
                if(trade.getCantProfit() != 0):
                    print(message)        
                    #bot.send_message(chat_id=config.TELEGRAM_CHANNEL ,text=message)
                else:
                    print(res['k']['c'])
    except BinanceAPIException as e:
        print(e)
        await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())