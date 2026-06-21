# 🏛️ Institutional Equity Valuation & M&A Screening Terminal

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Data Pipeline](https://img.shields.io/badge/Data%20Pipeline-yfinance%20API-gold.svg)](https://pypi.org/project/yfinance/)

## 📈 Executive Summary
This repository contains a full-stack, interactive **Equity Valuation and M&A Deal Screening Terminal** designed to automate the preliminary phases of corporate finance advisory and private equity workflows. 

By eliminating the manual friction of pulling financial statements from fragmented sources or expensive static data terminals, this application establishes an automated pipeline that ingests real-time market data, orchestrates historical trend analysis, calculates intrinsic/relative valuations, and compiles client-ready investment screening memos. 

---

## 🛠️ Core Financial Engines

### 1. Target Transaction Screener & M&A Scoring
* **Quantitative Baseline:** Instantly evaluates public targets by parsing core capital structure and operational metrics, including Enterprise Value (EV), Market Capitalization, LTM Revenue Growth, and LTM EBITDA Margins.
* **M&A Scorecard:** Computes a proprietary operational efficiency score to instantly flag high-margin, high-growth buyout or advisory targets.

### 2. Intrinsic Valuation Engine (Multi-Stage DCF Model)
* **Cash Flow Ingestion:** Automatically extracts 4 years of historical data to track trends across Total Revenue, EBITDA, and Free Cash Flow ($FCF = CFO + CapEx$).
* **Dynamic Sensitivity Analysis:** Features an interactive multi-stage Discounted Cash Flow (DCF) model allowing users to stress-test implied valuation ranges by dynamically manipulating the Weighted Average Cost of Capital (WACC), terminal multiples, and perpetual growth rates via front-end toggles.

### 3. Relative Valuation Matrix (Trading Comps)
* **Automated CCA Grid:** Executes a live Comparable Company Analysis (CCA) by mapping a custom user-defined peer group against the target asset.
* **Multiple Benchmarking:** Standardizes and ranks real-time trading multiples ($EV/EBITDA$, $EV/Revenue$, and $P/E$) across industry competitors to identify relative mispricings and premium/discount profiles.

### 4. Automated Investment Committee Memo Generation
* **Executive Deliverable:** Compiles automated quantitative findings into a structured, highly formatted Investment Screening Memo. 
* **One-Click Export:** Allows junior bankers or investment professionals to instantly download the generated report as a file for immediate distribution or pipeline logging.

---

## 💻 Tech Stack & Architecture

* **Frontend Framework:** `Streamlit` (Architected for scalable, low-latency financial dashboards)
* **Data Engineering & Pipeling:** `yfinance API` (Structured for dynamic financial statement extraction and automated error handling/caching)
* **Vectorized Financial Modeling:** `Pandas` & `NumPy`
* **Data Visualization:** `Plotly Express` (Interactive financial charts, trend lines, and multiple benchmarking)

```text
├── app.py                  # Core application entry point and UI Layout orchestration
├── requirements.txt        # Enterprise dependency manifest
├── screens/
│   └── screener.py         # Financial data ingestion engine and API exception mapping
└── valuation/
    └── metrics.py          # Quantitative scoring and multi-stage DCF valuation logic

---

### 🚀 Local Installation & Deployment

*(Note: For enterprise code auditing or local execution, the platform can be initialized via terminal using the single block below.)*

```bash
# 1. Clone the Infrastructure Repository and navigate inside
git clone [https://github.com/YOUR_GITHUB_USERNAME/pe-deal-screener.git](https://github.com/YOUR_GITHUB_USERNAME/pe-deal-screener.git)
cd pe-deal-screener

# 2. Initialize and Activate Isolated Virtual Environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Package Dependencies
pip install -r requirements.txt

# 4. Launch Local Web Server
streamlit run app.py
