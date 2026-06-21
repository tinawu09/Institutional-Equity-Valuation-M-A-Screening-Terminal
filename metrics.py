def screen_company(data):
    return True

def acquisition_score(data):
    growth = data.get("Revenue Growth", 0) or 0
    margin = data.get("EBITDA Margin", 0) or 0
    pe_ratio = data.get("PE Ratio", 30) or 30

    score = (growth * 40) + (margin * 40) + (max(0, 40 - pe_ratio) * 0.5)
    return round(score, 2)

def recommendation(score):
    if score >= 20: return "Strong Candidate"
    elif score >= 10: return "Potential Candidate"
    else: return "Monitor"

def run_dcf_model(data, growth_rate=0.06, wacc=0.09, terminal_growth=0.025):
    """Calculates Intrinsic Value per share using a 5-Year Unlevered DCF model."""
    trends = data.get("Historical_Trends", {})
    fcf_history = trends.get("FCF", [])
    
    # Use latest historical FCF as baseline, fallback to an estimated 10% of Revenue
    base_fcf = fcf_history[-1] if fcf_history else (data.get("Market Cap", 0) * 0.04)
    if base_fcf <= 0:
        base_fcf = data.get("Market Cap", 0) * 0.04 # Fallback floor if net negative FCF
        
    # Project 5 years of future Free Cash Flows
    projected_fcf = []
    discount_factors = []
    present_values = []
    
    for year in range(1, 6):
        fcf_next = base_fcf * ((1 + growth_rate) ** year)
        df = 1 / ((1 + wacc) ** year)
        projected_fcf.append(fcf_next)
        discount_factors.append(df)
        present_values.append(fcf_next * df)
        
    # Terminal Value calculation (Gordon Growth Method)
    terminal_value = (projected_fcf[-1] * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_of_terminal_value = terminal_value * discount_factors[-1]
    
    # Enterprise Value & Equity Value Enterprise calculation
    enterprise_value = sum(present_values) + pv_of_terminal_value
    equity_value = enterprise_value - data["Total Debt"] + data["Total Cash"]
    
    # Intrinsic value per share
    intrinsic_value = equity_value / data["Shares Outstanding"]
    upside = ((intrinsic_value / data["Current Price"]) - 1) if data["Current Price"] > 0 else 0
    
    return {
        "Intrinsic Value": round(intrinsic_value, 2),
        "Enterprise Value": enterprise_value,
        "Equity Value": equity_value,
        "Upside": round(upside * 100, 2)
    }

def run_cca_model(target, peers_data):
    """Compares target multiples against peer group averages."""
    if not peers_data:
        return {}
        
    avg_pe = sum([p["PE Ratio"] for p in peers_data]) / len(peers_data)
    avg_ev_rev = sum([p["EV Revenue"] for p in peers_data]) / len(peers_data)
    avg_ev_ebitda = sum([p["EV EBITDA"] for p in peers_data]) / len(peers_data)
    
    return {
        "Peer Avg P/E": round(avg_pe, 2),
        "Peer Avg EV/Rev": round(avg_ev_rev, 2),
        "Peer Avg EV/EBITDA": round(avg_ev_ebitda, 2),
        "P/E Premium/Discount": round(((target["PE Ratio"] / avg_pe) - 1) * 100, 1) if avg_pe > 0 else 0,
        "EV/EBITDA Premium/Discount": round(((target["EV EBITDA"] / avg_ev_ebitda) - 1) * 100, 1) if avg_ev_ebitda > 0 else 0
    }

    