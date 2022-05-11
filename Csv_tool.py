import pandas as pd
import os
"""
{
  "e": "kline",     // Event type
  "E": 123456789,   // Event time
  "s": "BNBBTC",    // Symbol
  "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BNBBTC",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}

"""
class csv_tool:
    
    def __init__(self):
      self.columnas= ['s', 'i', 'o', 'c', 'h', 'l','v', 'n']
      self.columns_csv = ['Date','open', 'close', 'high', 'low','volume','number_of_trade']

    def escribriCsv(self,res,is_json=True, path = ''):
      if(is_json):
        df2 = pd.json_normalize(res['k'])
        df2 = df2.assign(E=res['E'])        
        df2 = df2.drop(['s','i','T','t','f','L','x','q','V','Q','V'], axis=1)
        df2 = df2.reindex(columns=['E','o', 'c', 'h', 'l','v','n'])
        df2.to_csv(path, index=None, mode="a", header=not os.path.isfile(path))
      else:
        df2 = pd.DataFrame(res,columns=['Date','open','high','low','close','volume','close_time',
                        'quote_asset_volum','number_of_trade','taker_buy_base','take_buy_quote','ignore'])
        df2 = df2.drop(['close_time','quote_asset_volum','taker_buy_base','take_buy_quote','ignore'], axis=1)
        df2 = df2[['Date','open', 'close', 'high', 'low','volume','number_of_trade']]
        df2.to_csv(path, index=None, mode="a", header=not os.path.isfile(path))
      

    def leerCsv(self,res):
        self.klines = pd.read_csv('csv/'+ res['k']['s'] + '_' + res['k']['i']+'.csv')
        self.klines    = pd.DataFrame(self.klines,columns=self.columns_csv)        
        return self.klines
    
    def filasCsv(self,res):
        result = pd.read_csv('csv/'+ res['k']['s'] + '_' + res['k']['i']+'.csv')
        return len(result)

