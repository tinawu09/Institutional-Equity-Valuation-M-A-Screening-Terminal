import streamlit as st
import pandas as pd
import plotly.express as px

from screens.screener import get_full_company_data
from valuation.metrics import (
    screen_company, acquisition_score, recommendation, run_dcf_model, run_cca_model
)

st.set_page_config(page_title="Institutional PE Screener", layout="wide")
st.title("🏛️ Private Equity Deal Screening & Valuation Platform")

# --- NEW: Short & Sweet Instructions ---
st.markdown("""
**Welcome to the PE Screening Terminal.**
* 🎯 **Target Assessment:** Enter a primary ticker to generate a baseline M&A score.
* 📊 **Financials & DCF:** Review 4-year historical trends and simulate intrinsic value.
* ⚖️ **Peer Comps:** Compare target trading multiples against competitors.
* 📄 **Export Memo:** Generate and download a formatted investment screening report.
---
""")

# Sidebar navigation / Inputs
st.sidebar.header("Platform Parameters")
target_ticker = st.sidebar.text_input("Target Company Ticker:", "MSFT").strip().upper()
peer_tickers_input = st.sidebar.text_input("Comparable Peer Group (Commas):", "AAPL, GOOGL, AMZN, ORCL")
peer_tickers = [p.strip().upper() for p in peer_tickers_input.split(",") if p.strip()]

# Load Core Data
with st.spinner("Fetching metrics..."):
    target_data = get_full_company_data(target_ticker)
    peers_list = []
    for peer in peer_tickers:
        p_data = get_full_company_data(peer)
        if p_data: peers_list.append(p_data)

if target_data:
    # Top Level Screening Evaluation Status Ribbon
    score = acquisition_score(target_data)
    rec_status = recommendation(score)
    target_data["Score"] = score
    target_data["Recommendation"] = rec_status

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Target Asset", target_data["Company"])
    col2.metric("Current Market Price", f"${round(target_data['Current Price'], 2)}")
    col3.metric("Deal Target Score", f"{score} / 100")
    col4.subheader(f"Status: **{rec_status}**")

    # Create UI Core Workspaces tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Financial Trend Dashboard", "🔑 DCF Valuation Module", "📈 Comparable Company Analysis (CCA)", "📄 Investment Memo Generator"
    ])

    # TAB 1: FINANCIAL HISTORICAL DASHBOARD
    with tab1:
        st.subheader("Historical Corporate Financial Trends")
        trends = target_data.get("Historical_Trends", {})
        if trends and "Years" in trends:
            trend_df = pd.DataFrame({
                "Year": trends["Years"],
                "Revenue ($B)": [r / 1e9 for r in trends["Revenue"]],
                "EBITDA ($B)": [e / 1e9 for e in trends["EBITDA"]],
                "Free Cash Flow ($B)": [f / 1e9 for f in trends["FCF"]]
            })
            st.dataframe(trend_df, use_container_width=True)
            
            melted_df = trend_df.melt(id_vars="Year", var_name="Metric", value_name="Amount ($ Billions)")
            fig = px.line(melted_df, x="Year", y="Amount ($ Billions)", color="Metric", markers=True, title="Core Historical Financial Trajectory")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Historical financial statement records are limited for this asset.")

    # TAB 2: INTRINSIC VALUE DCF MODULE
    with tab2:
        st.subheader("Discounted Cash Flow Intrinsic Value Evaluation Simulator")
        c1, c2, c3 = st.columns(3)
        g_rate = c1.slider("Pro-Forma FCF Growth Rate (Y1-Y5)", 0.01, 0.40, 0.08, step=0.01)
        wacc_rate = c2.slider("Weighted Average Cost of Capital (WACC)", 0.05, 0.20, 0.09, step=0.01)
        term_rate = c3.slider("Terminal Perpetuity Growth Rate (g)", 0.005, 0.05, 0.025, step=0.005)
        
        dcf_results = run_dcf_model(target_data, growth_rate=g_rate, wacc=wacc_rate, terminal_growth=term_rate)
        
        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("Estimated Intrinsic Per-Share Fair Value", f"${dcf_results['Intrinsic Value']}")
        dc2.metric("Market Discount / Premium Implied Upside", f"{dcf_results['Upside']}%")
        
        if dcf_results['Upside'] > 0:
            st.success("Asset is currently trading at an implied discount to intrinsic value.")
        else:
            st.warning("Asset market price commands a valuation premium relative to DCF baseline parameters.")

    # TAB 3: COMPARABLE COMPANY ANALYSIS (CCA)
    with tab3:
        st.subheader("Comparable Peer Universe Valuation Multiples Trading Grid")
        if peers_list:
            combined_trading_pool = [target_data] + peers_list
            cca_table_data = [{
                "Ticker": item["Ticker"],
                "Company": item["Company"],
                "P/E Multiple": round(item["PE Ratio"], 2),
                "EV / Revenue": round(item["EV Revenue"], 2),
                "EV / EBITDA": round(item["EV EBITDA"], 2),
                "Market Cap ($B)": round(item["Market Cap"] / 1e9, 2)
            } for item in combined_trading_pool]
            
            cca_df = pd.DataFrame(cca_table_data)
            st.dataframe(cca_df, use_container_width=True)
            
            cca_analytics = run_cca_model(target_data, peers_list)
            st.markdown("### Valuation Discontinuity Diagnostic Summary")
            cc1, cc2 = st.columns(2)
            cc1.write(f"**Peer Group Mean Trading P/E Multiplier Floor:** {cca_analytics['Peer Avg P/E']}x")
            cc1.write(f"**Target Premium/Discount vs Average Peer Base:** {cca_analytics['P/E Premium/Discount']}%")
            cc2.write(f"**Peer Group Mean EV/EBITDA Transaction Multiple:** {cca_analytics['Peer Avg EV/EBITDA']}x")
            cc2.write(f"**Target EV/EBITDA Vector Delta Deviation:** {cca_analytics['EV/EBITDA Premium/Discount']}%")
        else:
            st.warning("Please supply valid alternative trading tickers to run relative multiples analysis.")

    # TAB 4: ANALYST REPORT GENERATOR
    with tab4:
        st.subheader("Generate Institutional Transaction Screening Memorandum")
        
        memo_content = f"""INVESTMENT SCREENING MEMORANDUM: {target_data['Company'].upper()} ({target_data['Ticker']})
---------------------------------------------------------------------------------
TARGET RISK CLASSIFICATION: {rec_status.upper()} | PLATFORM SCORE: {score}/100

1. CORE FINANCIAL STANDING PROFILE
- Market Valuation Capitalization: ${round(target_data['Market Cap']/1e9, 2)}B
- Trailing Top-line Revenue Growth Factor: {round(target_data['Revenue Growth']*100, 2)}%
- Consolidated EBITDA Operating Efficiency Margin: {round(target_data['EBITDA Margin']*100, 2)}%
- Implied Trailing Market Price to Earnings multiple: {round(target_data['PE Ratio'], 2)}x

2. DCF VALUE PROJECTION SIGNALS (WACC: {wacc_rate*100}%, Growth: {g_rate*100}%)
- Model Computed Per-Share Fair Intrinsic Value Baseline: ${dcf_results['Intrinsic Value']}
- Implied Under/Over-Valuation Variance Delta: {dcf_results['Upside']}%

3. RELATIVE PEER COMPARABLE ANALYSIS
- Target Peer Enterprise Value Multiples (EV/EBITDA): {round(target_data['EV EBITDA'], 2)}x 
- Structural Valuation Vector Delta Deviation: {cca_analytics.get('EV/EBITDA Premium/Discount', 0)}%

---------------------------------------------------------------------------------
CONFIDENTIALITY NOTE: FOR INTERNAL PRIVATE EQUITY INVESTMENT COMMITTEE EVALUATION USE ONLY."""

        st.text_area("Live Memo Text Canvas Markdown Preview Container", memo_content, height=350)
        
        st.download_button(
            label="💾 Download Investment Screening Report (.TXT)",
            data=memo_content,
            file_name=f"{target_data['Ticker']}_PE_Screening_Memo.txt",
            mime="text/plain"
        )
else:
    st.error("Invalid ticker string provided or system rate-limiting restriction encountered on target request.")
    