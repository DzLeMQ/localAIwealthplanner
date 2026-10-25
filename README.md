# Local AI Wealth Growth Planner
Local AI Wealth Planner & Interactive Visualiser is a privacy-first, locally hosted financial forecasting and analysis web application. Built using Streamlit, LangChain, and Ollama, the application allows users to simulate long-term portfolio growth while strictly accounting for real-world inflation. Unlike traditional calculators, it integrates a local Large Language Model (LLM) to deliver automated, professional-grade macroeconomic commentary tailored to the Australian market without exposing sensitive financial data to cloud-based APIs.

# Key Features

* 100% Local AI Inference: Uses LangChain and Ollama (supporting models like Milo and Llama) to process financial data and generate strategic analysis entirely on your local machine.
* Live Australian Macroeconomic Scraper: Built-in web scraping engine utilising BeautifulSoup to fetch live inflation data directly from the Reserve Bank of Australia (RBA) homepage to auto-calibrate baseline metrics.
* Inflation-Adjusted Calculation Engine: Simulates compound growth paths over up to 50 years, calculating both Nominal Value and Real Value (Today's Buying Power) side-by-side.
* Safe Withdrawal Rate (SWR) Simulator: Models monthly passive income targets using customizable SWR limits and flags long-term nest egg sustainability.
* Interactive Visualisations: Renders dual-line time-series projection charts using pandas and Streamlit's native charting to clearly map out the "inflation gap" over time.

_Note: Milo:latest is my custom model._

# Core Tech Stack

* Frontend & Dashboard: Streamlit
* AI Framework: LangChain / ChatOllama
* Data Processing: Pandas
* Web Scraping: Requests & BeautifulSoup4


# Front-end Quick Glance
<img width="913" height="313" alt="image" src="https://github.com/user-attachments/assets/cdbdced3-43b6-477e-9371-de1043e530e6" />

<img width="925" height="314" alt="image" src="https://github.com/user-attachments/assets/66c6826d-a96c-410e-a49e-e11dce01ed80" />

<img width="931" height="484" alt="image" src="https://github.com/user-attachments/assets/70297a17-a4a1-410f-82d7-779a36109480" />

## ⚠ Disclaimer & Risk Warning
I developed this strictly for educational purposes and use it as my own personal planner. Projections are simulated and do not guarantee future results. Users are responsible for evaluating financial risks.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
