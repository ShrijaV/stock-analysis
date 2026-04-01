from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


companies = ["INFY.NS", "TCS.NS", "RELIANCE.NS"]

def get_stock_data(symbol):
    data = pd.read_csv(f"files/{symbol}.csv")

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.dropna()

    data['Daily Return'] = (data['Close'] - data['Open']) / data['Open']
    data['MA_7'] = data['Close'].rolling(7).mean()

    return data



@app.get("/companies")
def get_companies():
    return {"companies": companies}


@app.get("/data/{symbol}")
def get_data(symbol: str):
    symbol=symbol.upper()
    if not symbol.endswith(".NS"):
        symbol=symbol+".NS"
    if symbol not in companies:
        return {"error": "Invalid symbol"}
    
    data = get_stock_data(symbol)
    if isinstance(data, dict):
        return data
    return data.tail(30).to_dict(orient="records")


@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    symbol=symbol.upper()
    if not symbol.endswith(".NS"):
        symbol=symbol+".NS"
    data = get_stock_data(symbol)
    if isinstance(data, dict):
        return data
    summary = {
        "52_week_high": float(data['High'].max()),
        "52_week_low": float(data['Low'].min()),
        "average_close": float(data['Close'].mean())
    }

    return summary

@app.get("/compare/{s1}/{s2}")
def compare(s1:str, s2:str):
    s1=s1.upper()
    s2=s2.upper()
    if not s1.endswith(".NS"):
        s1=s1+".NS"
    if not s2.endswith(".NS"):
        s2=s2+".NS"
    data1 = get_stock_data(s1)
    data2 = get_stock_data(s2)
    return{
        "s1":s1,
        "s2":s2,
        "avg_close_1":float(data1['Close'].mean()),
        "avg_close_2":float(data2['Close'].mean()),
        "volatility_1": float(data1['Daily Return'].std()),
        "volatility_2": float(data2['Daily Return'].std())
    }

