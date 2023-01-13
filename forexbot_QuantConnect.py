# region imports
from AlgorithmImports import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from QuantConnect.Data.Custom import *
# endregion

class CryingFluorescentPinkHorse(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2018,1,1)
        self.SetEndDate(2022,1,31)
        self.SetCash(100000)
        self.EURUSD = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda).Symbol
        history = self.History([self.EURUSD], 20, Resolution.Hour)
        self.df = pd.DataFrame(history.loc[self.EURUSD].close)
        self.df.rename(columns={'close':'c'}, inplace=True)

    def OnData(self, data):
        self.df = self.df.append(pd.DataFrame({'c':[data[self.EURUSD].Close]}, index=[data[self.EURUSD].Time]))
        self.df["short_ma"] = self.df["c"].rolling(window=20).mean()
        self.df["long_ma"] = self.df["c"].rolling(window=50).mean()
        delta = self.df["c"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        self.df["rsi"] = rsi
        self.df["signal"] = np.where(self.df["short_ma"] > self.df["long_ma"], 1, 0)
        self.df["signal"] = np.where(self.df["short_ma"] < self.df["long_ma"], -1, self.df["signal"])
        self.df["signal"] = np.where((self.df["rsi"] < 30) & (self.df["signal"] != -1), 1, self.df["signal"])
        self.df["signal"] = np.where((self.df["rsi"] > 70) & (self.df["signal"] != 1), -1, self.df["signal"])
        
        if self.df["signal"].iloc[-1] == 1:
            self.SetHoldings(self.EURUSD, 1)
        elif self.df["signal"].iloc[-1] == -1:
            self.Liquidate()
            
