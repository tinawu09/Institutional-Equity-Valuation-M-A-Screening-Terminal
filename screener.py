import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Streamlit will cache this for 1 hour to protect you
def get_full_company_data(ticker):
    try:
        # Reverted back to the standard call without the custom session
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) <= 1:
            print(f"No info returned for {ticker}")
            return None

        # Fetch Historical Financial Statements
        income_stmt = stock.income_stmt
        cash_flow = stock.cashflow

        # Extract Historical Trends safely
        trends = {}
        if not income_stmt.empty and not cash_flow.empty:
            years = [str(date.year) for date in income_stmt.columns[:4]]
            
            rev_row = income_stmt.get("Total Revenue") or income_stmt.get("Gross Revenue")
            trends["Revenue"] = rev_row.iloc[:4].tolist()[::-1] if rev_row is not None else [0]*4
            
            ebitda_row = income_stmt.get("EBITDA") or income_stmt.get("Operating Income")
            trends["EBITDA"] = ebitda_row.iloc[:4].tolist()[::-1] if ebitda_row is not None else [0]*4
            
            cfo_row = cash_flow.get("Operating Cash Flow") or cash_flow.get("Total Cash From Operating Activities")
            capex_row = cash_flow.get("Capital Expenditures")
            
            fcf_list = []
            for i in range(min(4, len(cash_flow.columns))):
                cfo = cfo_row.iloc[i] if cfo_row is not None else 0
                capex = capex_row.iloc[i] if capex_row is not None else 0
                fcf_list.append(cfo + capex) 
            trends["FCF"] = fcf_list[::-1]
            trends["Years"] = years[::-1]

        # Base Summary Data Dictionary
        data = {
            "Ticker": ticker,
            "Company": info.get("shortName", ticker),
            "Sector": info.get("sector", "N/A"),
            "Market Cap": info.get("marketCap", 0) or 0,
            "Revenue Growth": info.get("revenueGrowth", 0) or 0,
            "EBITDA Margin": info.get("ebitdaMargins", 0) or 0,
            "PE Ratio": info.get("trailingPE") or info.get("forwardPE") or 25.0,
            "EV Revenue": info.get("enterpriseToRevenue", 0) or 0,
            "EV EBITDA": info.get("enterpriseToEbitda", 0) or 0,
            "Shares Outstanding": info.get("sharesOutstanding") or 1,
            "Total Debt": info.get("totalDebt") or 0,
            "Total Cash": info.get("totalCash") or 0,
            "Current Price": info.get("currentPrice") or info.get("previousClose") or 0,
            "Historical_Trends": trends
        }
        return data
        
    except Exception as e:
        print(f"Error compiling data for {ticker}: {e}")
        return None
    