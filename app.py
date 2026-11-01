import streamlit as st
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
import re

import streamlit as st
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
import re

# Configureation and responsive css
st.set_page_config(
    page_title="Local AI Wealth Planner", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# There is an invisible header block before the page. This removes it and safely pulls subheader up
st.html(
    """
    <style>
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """
)
# Initialize Session State tracking layer for layout state toggle
if "show_in_page_settings" not in st.session_state:
    st.session_state.show_in_page_settings = False

# Web scrapper for rates
@st.cache_data(ttl=3600)  # cache 1 hour to ensure rapid updates when milestones land
def fetch_live_au_rates():
    """
    Scrapes the official RBA homepage for live inflation data 
    and returns a combined payload for national macro benchmarks.
    """
    # Default values if the RBA website not reachable
    metrics = {
        "inflation": 4.3,      
        "cash_rate": 4.60,      
        "highest_rate": 6.25    #au highest-interest rate (ING/Revolut)
    }
    try:
        url = "https://rba.gov.au"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')             
            import re
            for label in soup.find_all(string=re.compile(r'Consumer Price Index|Cash Rate')):
                parent = label.parent
                sibling = parent.find_next(string=re.compile(r'\d+\.\d+\s*%'))
                if sibling:
                    match = re.search(r'(\d+\.\d+)\s*%', sibling)
                    if match:
                        val = float(match.group(1))
                        if "Consumer Price Index" in label or "CPI" in label:
                            metrics["inflation"] = val
                        elif "Cash Rate" in label:
                            metrics["cash_rate"] = val
                                
        return metrics
    except Exception:
        return metrics

# Load live rates
macro_data = fetch_live_au_rates()
live_inflation = macro_data["inflation"]
# print(f"Live AU Inflation Rate: {live_inflation}%")
live_cash_rate = macro_data["cash_rate"]
live_highest_rate = macro_data["highest_rate"]

# Interface and layout
st.subheader("📊 Local AI Wealth Planner", anchor=False)

# st.markdown("---")
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.caption(
        f"Powered by AI — Running 100% Locally - Built with local LLMs | "
        f"Live AU Inflation Rate: {live_inflation}% | "
        f"RBA Cash Rate: {live_cash_rate}% | "
        f"Peak AU Savings Yield: {live_highest_rate}% p.a."
    )
with col_btn:
    if st.button("⚙️ Open/Close Strategic System Settings", type = "primary", use_container_width=True):
        st.session_state.show_in_page_settings = not st.session_state.show_in_page_settings

# Parameter settings
if st.session_state.show_in_page_settings:
    with st.container(border=True):
        st.markdown("#### 🛠️ Strategic System Configurations")
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            selected_model = st.selectbox("Select Model Options", ["Milo:latest", "llama:latest"], index=0, key="model_main")
            temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.0, value=0.8, step=0.1, key="temp_main")
        with col_ctrl2:
            withdrawal_rate = st.slider("Safe Withdrawal Rate (SWR %)", min_value=1.0, max_value=10.0, value=5.0, step=0.5, key="swr_main")
            inflation_rate = st.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=10.0, value=live_inflation, step=0.1, key="inf_main")
            
        st.markdown(
            """
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #E2E8F0;">
                <span style="font-size: 13px; color: #228B22;">
                    📊 <b>Privacy Note:</b> Calculations and model inferences run 100% locally on your machine. This app is equipped with local LLMs.
                </span>
            </div>
            """, unsafe_allow_html=True
        )
else:
    # fallbacks to prevent variable runtime name breaks when settings panel remains collapsed
    selected_model = "Milo:latest"
    temperature = 0.8
    withdrawal_rate = 5.0
    inflation_rate = live_inflation

# st.markdown("---")

# Calculation engine
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
        duration_display = "Indefinitely (Perpetual Nest Egg)"
    else:
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

# Dashboard - parameters and calculation pipeline runner
st.write("#### 📈 Plan Your Monthly Income")
st.write("Enter your metrics below to trigger your local AI engine and compounding calculations:")

principle_col, year_col, growth_col = st.columns(3, gap="small")
with principle_col:
    principal = st.number_input("Starting Principal ($)", min_value=0.0, value=150000.0, step=10000.0)
with year_col:
    years = st.number_input("Years to Grow", min_value=1, max_value=50, value=15)
with growth_col:
    growth = st.number_input("Expected Annual Return (%)", min_value=0.0, max_value=30.0, value=live_highest_rate, step=0.1)


st.markdown(
    """
    <style>
    /* Target only the button that contains your specific key context */
    div[data-testid="stButton"] > button[key="growth_plan_btn"] {
        background-color: #CC3300 !important;
        color: white !important;
        border-radius: 4px;
    }
    div[data-testid="stButton"] > button[key="growth_plan_btn"]:hover {
        background-color: #CC8800 !important;
        color: white !important;
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
            
            analyse_col, chart_col = st.columns(2, gap="medium")
            
            with analyse_col:
                st.success("#### 📊 Inflation-Adjusted Milestones")
                st.write(f"**Projected End Value (Nominal):** `${metrics['future_nominal']:,.2f}`")
                st.write(f"**Projected Buying Power (Real Value):** `${metrics['future_real']:,.2f}`")
                st.write(f"**Stable Monthly Income (In Today's Buying Power):** `${metrics['monthly_real_income']:,.2f}/month`")
                st.write(f"**Income Sustainability Period:** `{metrics['duration_display']}`")
                
                st.write("#### 🤖 Local AI Strategic Commentary")
                st.write(ai_analysis)

            with chart_col:
                st.success("#### 📈 Real vs. Nominal Growth Projections")

                raw_df = pd.DataFrame(metrics["chart_points"])
                chart_df = pd.DataFrame({
                    "Year": raw_df["Year"],
                    "Nominal Value": raw_df["Nominal Value (Face Value)"],
                    "Today's Buying Power": raw_df["Real Value (Today's Buying Power)"]
                }).set_index("Year")

                st.line_chart(
                    chart_df,
                    x_label="Timeline (Years)",
                    y_label="Balance ($ AUD)",
                     color=["#FF4B4B", "#1F77B4"],     
                    height=320
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
            #### 🔒 Privacy Protection Active: 
            
            **Why are you seeing this message?**
            To guarantee absolute data privacy, this application is engineered to 
            run exclusively on your local machine. 

            It is currently deployed on the **Streamlit Community Cloud**, 
            an environment where it is strictly restricted from processing your 
            personal financial data or banking profiles to prevent any public cloud exposure.

            **How to safely run your wealth planner:**
            Follow the instructions below to quickly launch this secure workspace 
            on your own local device. Once configured, your private AI financial 
            strategist will be ready to help you map out your wealth generation plan!
            
            #### How to run this app locally:

            1. **[💻 Clone the repository](https://github.com)** to your local machine.
            2. **Install the requirements** inside your virtual environment:
            ```bash
            pip install -r requirements.txt
            ```
            3. **Make sure your local LLM server is running.**
            4. **Launch the app locally** using your terminal:
            ```bash
            streamlit run app.py
            ```
            """)

            
           
