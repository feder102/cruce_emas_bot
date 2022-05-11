import asyncio
import os
import config
import telegram
import pandas as pd
import numpy as np 
import macd,fedestrat,fedestrat_backtesting
from Csv_tool import csv_tool
from binance import AsyncClient, BinanceSocketManager,Client
from binance.exceptions import BinanceAPIException

#SEGUIR CON EL DINERO QUE LE MANDO QUE NO SE CREE EN LA CLASE RSI SINO ACA EN EL MAIN

def main():
    bot = telegram.Bot(token=config.TELEGRAM_TOKEN)
    interval = '5m'
    #macd.tradingstrat('BTCUSDT', interval,qty=0.00001)
    fedestrat.tradingstrat('BTCUSDT', interval,qty=0.00001)
    #fedestrat_backtesting.tradingstrat('BTCUSDT', interval,qty=0.00001)
    

if __name__ == "__main__":
    #PARA REAL
    while True:
        print("Ejecuntandose")
        main()
    #PARA BACTESTING
    #print("Ejecuntandose")
    #main()