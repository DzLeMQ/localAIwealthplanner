import streamlit as st
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama


st.set_page_config(page_title="Local AI Wealth Planner", 
                   page_icon="📊", 
                   layout="wide",
                   initial_sidebar_state="expanded")

# live rates by scrapper
@st.cache_data(ttl=86400)  # Cache metrics for 24 hours to maximize performance
def fetch_live_au_macro_metrics():
    """
    Scrapes the official RBA homepage for live inflation data 
    and returns a combined payload for national macro benchmarks.
    """
    metrics = {
        "inflation": 4.0,       # Current RBA Target Cycle baseline
        "highest_rate": 6.25    # Top Australian High-Interest Variable Yield (ING/Revolut)
    }
    try:
        url = "https://rba.gov.au"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for container in soup.find_all(text=True):
                if "Consumer Price Index" in container:
                    parent = container.parent
                    sibling_text = parent.find_next_sibling() or parent.find_next()
                    if sibling_text:
                        clean_rate = sibling_text.text.replace('%', '').strip()
                        metrics["inflation"] = float(clean_rate)
                        break
        return metrics
    except Exception:
        return metrics  

# Load live rates
macro_data = fetch_live_au_macro_metrics()
live_inflation = macro_data["inflation"]
live_highest_rate = macro_data["highest_rate"]

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    header {
        visibility: hidden;
        height: 0px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Local AI Wealth Planner")
st.caption(
    f"Powered by LLMs — Running 100% Locally | "
    f"Live AU Inflation Rate: {live_inflation}% | "
    f"Peak AU Savings Yield: {live_highest_rate}% p.a."
)

# Sidebar setting
st.sidebar.markdown(
    '<span style="font-size: 16px; color: #2EBB57; font-weight: 600;">🛠️Environment Settings</span>', 
    unsafe_allow_html=True
)
selected_model = st.sidebar.selectbox("Select Model", ["Milo:latest", "llama:latest"], index=0)
temperature = st.sidebar.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.8, step=0.1)

st.sidebar.markdown(
    '<span style="font-size: 16px; color: #2EBB57; font-weight: 600;">📈 Withdrawal & Inflation Settings</span>', 
    unsafe_allow_html=True
)
withdrawal_rate = st.sidebar.slider("Safe Withdrawal Rate (SWR %)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
inflation_rate = st.sidebar.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=10.0, value=live_inflation, step=0.1)


st.sidebar.markdown(
    """
    
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #333333;">
            <span style="text-decoration: none; font-size: 14px; font-weight: 400; color: #228B22">
                📊 Local AI Wealth Planner is a privacy-first wealth planner
                  hosted entirely on your local machine. Built using Streamlit, LangChain, and Ollama,
                    it simulates long-term portfolio growth adjusted for real-world inflation. 
                    By integrating a local LLM, the application delivers tailored, professional 
                    macroeconomic commentary for the Australian market as well as keeping your 
                    financial data 100% private and safe from cloud APIs.
            </span>
    </div>

    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #333333;">
        <a href="https://github.com/DzLeMQ/localAIwealthplanner" target="_blank" 
           style="text-decoration: none; font-size: 15px; font-weight: 500; color: #228B22;">
            💻 View Code on GitHub
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
# 1. inflation adjusted calculation engine
def calculate_financial_plan(starting_principal, years_to_grow, annual_growth_rate, swr_rate, inflation_rate):
    r_nominal = annual_growth_rate / 100.0
    r_real = (annual_growth_rate - inflation_rate) / 100.0
    swr = swr_rate / 100.0
    n = 12
    
    yearly_data = []
    current_nominal = starting_principal
    current_real = starting_principal
    yearly_data.append({
        "Year": 0, 
        "Nominal Value (Face Value)": round(current_nominal, 2),
        "Real Value (Today's Buying Power)": round(current_real, 2)
    })
    
    for year in range(1, years_to_grow + 1):
        current_nominal = current_nominal * ((1 + r_nominal/n) ** n)
        current_real = current_real * ((1 + r_real/n) ** n)
        
        yearly_data.append({
            "Year": year, 
            "Nominal Value (Face Value)": round(current_nominal, 2),
            "Real Value (Today's Buying Power)": round(current_real, 2)
        })
        
    future_real_value = current_real
    annual_real_income = future_real_value * swr
    monthly_real_income = annual_real_income / 12

    if monthly_real_income <= 0:
        duration_display = "0 Years"
    elif swr <= r_real:
        # If withdrawal rate is lower than or equal to inflation-adjusted return, the core fund stays intact
        duration_display = "Indefinitely (Perpetual Nest Egg)"
    else:
        # If withdrawal rate exceeds the real return, calculate how many years until drawdown hits zero
        years_it_lasts = future_real_value / annual_real_income
        duration_display = f"{years_it_lasts:.1f} Years"

    return {
        "starting": starting_principal,
        "years": years_to_grow,
        "nominal_rate": annual_growth_rate,
        "inflation_rate": inflation_rate,
        "future_nominal": current_nominal,
        "future_real": future_real_value,
        "monthly_real_income": monthly_real_income,
        "duration_display": duration_display,
        "chart_points": yearly_data
    }

#2. Prompts and parameter inputs

st.write("### 📈 Plan Your Monthly Income Target")
st.write("Enter your metrics below to trigger your local AI engine and compounding calculations:")

principle_col, year_col, growth_col = st.columns(3)
with principle_col:
    principal = st.number_input("Starting Principal ($)", min_value=0.0, value=200000.0, step=10000.0)
with year_col:
    years = st.number_input("Years to Grow", min_value=1, max_value=50, value=10)
with growth_col:
    growth = st.number_input("Expected Annual Return (%)", min_value=0.0, max_value=30.0, value=live_highest_rate, step=0.1)

# 3. processing pipeline

st.markdown(    """
    <style>
    .st-key-growth_plan_btn button, .stkey-growth_plan_btn button {
        background-color: #CC3300 !important;
        color: white !important;
    }
    .st-key-growth_plan_btn button:hover, .stkey-growth_plan_btn button:hover {
        background-color: #CC8800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
if st.button("⚡ Generate Strategic Growth Plan", type="primary", key="growth_plan_btn"):
    with st.spinner("Running calculation engines and waiting for local model inference..."):
        try:
            metrics = calculate_financial_plan(principal, int(years), growth, withdrawal_rate, inflation_rate)
            
            llm = ChatOllama(model=selected_model, temperature=temperature)
            
            system_prompt = (
                "You are an elite, highly professional Financial Strategist specialising in Australian markets. "
                "A deterministic calculator has computed inflation-adjusted numbers for a user's portfolio. "
                "Your job is to analyse these results and write a concise, 2-paragraph strategic analysis.\n\n"
                "CRITICAL RENDERING RULES:\n"
                "1. Explicitly context-match their selected expected growth against the live top Australian bank return "
                f"rate of {live_highest_rate}%.\n"
                "2. Point out the clear gap between Nominal face value growth and Real buying power metrics.\n"
                "3. Explain how the Monthly Income figure is represented in today's cost-of-living purchasing power.\n"
                "4. Maintain an objective tone. Do not provide personalised financial advice."
                "5. Use only Australian financial terminolog, english and context."
                
            )
            
            user_prompt = f"""
            Here are the calculated metrics:
            - Starting Capital: ${metrics['starting']:,.2f}
            - Timeline: {metrics['years']} years
            - Expected Growth: {metrics['nominal_rate']}% with an assumed {metrics['inflation_rate']}% inflation rate.
            - Projected Face Value (Nominal): ${metrics['future_nominal']:,.2f}
            - Projected Buying Power (Real): ${metrics['future_real']:,.2f}
            - Inflation-Adjusted Payout: ${metrics['monthly_real_income']:,.2f} per month in today's money value using a {withdrawal_rate}% Safe Withdrawal Rate.
            
            Provide a professional analysis of these results.
            """
            
            ai_analysis = llm.invoke([
                ("system", system_prompt),
                ("human", user_prompt)
            ]).content
            
            analyse_col, chart_col = st.columns(2)
            
            with analyse_col:
                st.success("### 📊 Inflation-Adjusted Milestones")
                st.write(f"**Projected End Value (Nominal):** `${metrics['future_nominal']:,.2f}`")
                st.write(f"**Projected Buying Power (Real Value):** `${metrics['future_real']:,.2f}`")
                st.write(f"**Stable Monthly Income (In Today's Buying Power):** `${metrics['monthly_real_income']:,.2f}/month`")
                st.write(f"**Income Sustainability Period:** `{metrics['duration_display']}`")
                
                st.write("### 🤖 Local AI Strategic Commentary")
                st.write(ai_analysis)
                    
            with chart_col:
                st.write("### 📈 Real vs. Nominal Growth Projections")                
                                
                # Convert your raw calculation tracking points into a Pandas DataFrame
                raw_df = pd.DataFrame(metrics["chart_points"])
                
                chart_df = pd.DataFrame({
                    "Year": raw_df["Year"],
                    "Nominal Value": raw_df["Nominal Value (Face Value)"],
                    "Today's Buying Power": raw_df["Real Value (Today's Buying Power)"]
              
                })
                
                # Set your investment timeline index
                chart_df = chart_df.set_index("Year")
                
                # Plot the native line chart safely
                st.line_chart(
                    chart_df,
                    x_label="Investment Timeline (Years)",
                    y_label="Portfolio Balance ($ AUD)",
                    color=["#ff4b4b", "#1f77b4"] 
                )

               
                st.write("")
                st.divider() 
                st.warning(
                    "⚠️ **Disclaimer & Risk Warning:** This application is powered by a local large language model "  
                    "and was built strictly for my personal wealth "
                    "planning, and educational purposes. All projections are simulated, based on hypothetical models, "
                    "and do not guarantee future results. Anyone running this code or evaluating these models must independently verify the logic. "
                    "Users are entirely responsible for accounting for market volatility and evaluating all "
                    "financial risks before making investment decisions."
                )
        except Exception as e:
            st.error("⚠️ **This application requires a local environment to run.**")
            
            st.markdown("""
            ### Why am I seeing this?
            This app is currently running on **Streamlit Community Cloud**, 
            which does not have access to your local computer's hardware or 
            locally installed language models (like Ollama, Llama.cpp, or LM Studio).
            
            ### How to run this app locally:
            1. **Clone the repository** to your local machine.
            2. **Install the requirements** inside your virtual environment:
            ```bash
            pip install -r requirements.txt
            ```
            3. **Make sure your local LLM server is running**.
            4. **Launch the app locally** using your terminal:
            ```bash
            streamlit run app.py
            ```
            """)
            
           