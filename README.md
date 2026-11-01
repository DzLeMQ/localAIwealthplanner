# Local AI Wealth Planner
Local AI Wealth Planner is a privacy-first, locally hosted financial forecasting and analysis web application. Built using Streamlit, LangChain, and Ollama, the application allows users to simulate long-term portfolio growth while strictly accounting for real-world inflation. Unlike traditional calculators, it integrates a local Large Language Model (LLM) to deliver automated, professional-grade macroeconomic commentary tailored to the Australian market without exposing sensitive financial data to cloud-based APIs.

# Key Features

* 100% Local AI Inference: Uses LangChain and Ollama (supporting models like Milo and Llama) to process financial data and generate strategic analysis entirely on your local machine.
* Live Australian Macroeconomic Scraper: Built-in web scraping engine utilising BeautifulSoup to fetch live inflation data directly from the Reserve Bank of Australia (RBA) homepage to auto-calibrate baseline metrics.
* Inflation-Adjusted Calculation Engine: Simulates compound growth paths over up to 50 years, calculating both Nominal Value and Real Value (Today's Buying Power) side-by-side.
* Safe Withdrawal Rate (SWR) Simulator: Models monthly passive income targets using customisable SWR limits and flags long-term nest egg sustainability.
* Interactive Visualisations: Renders dual-line time-series projection charts using pandas and Streamlit's native charting to clearly map out the "inflation gap" over time.

_Note: Milo:latest is my custom model._

# Core Tech Stack

* Frontend & Dashboard: Streamlit
* AI Framework: LangChain / ChatOllama
* Data Processing: Pandas
* Web Scraping: Requests & BeautifulSoup4


# Front-end at a Glance

<a href="https://localaiwealthplanner-9ssnpxappumba3bmbbpwb7v.streamlit.app/">Local AI Wealth Planner</a>

<img width="893" height="394" alt="image" src="https://github.com/user-attachments/assets/bb769d23-6693-49f1-8661-f87a041d2849" />

<img width="910" height="473" alt="image" src="https://github.com/user-attachments/assets/47d3acbb-da09-4477-87f1-02c159df645d" />


## ⚠ Disclaimer & Risk Warning
This project was developed strictly for educational purposes and personal wealth planning. All metrics, data, and charts shown in the accompanying images are simulated, fictional examples used for illustrative purposes only and do not represent actual financial accounts or real-world performance. Projections derived from this app are hypothetical and do not guarantee future results. Users are responsible for evaluating their own financial risks.


# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
