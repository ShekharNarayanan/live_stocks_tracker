# 📉📈 Live Stocks Tracker

A simple Streamlit web-app to scan US large-, mid- and small-cap universes for the **top losers & gainers** over a customizable look-back window. Powered by [yfinance](https://pypi.org/project/yfinance/) and Wikipedia scrapes—no paid API keys required.

---
## 🚀 Features

### General Scanner
- Look at the **general scanner** - explore the 20 winners and losers in all universes! 😎
- Observe essential information for each ticker such as % change, 14-RSI and 30 day volume 🌳

### Portfolio/ Watchlist
**New!**
- Log in with gmail to create your own personalized watchlist!
- Continue anonymously if you are just looking to explore the feature!
- **More to come soon!**


---
## Scanner peak:
<!---explore scanner video --->
![usage](media/usage_gif_scanner.gif)


## Portfolio peak:
<!---explore scanner video --->
![usage](media/usage_gif_portfolio.gif)

## 🚀 Getting Started

### 1. Clone this repo  
```bash
git clone https://github.com/ShekharNarayanan/live-stocks-tracker.git
cd live-stocks-tracker/
```

### 2. Install dependencies  
Create and activate a virtual environment, then install:
```bash
conda env create --file environment.portable.yml

```

### 3. Run the app  
```bash
streamlit run src/live_stocks_tracker/Home.py
```
This opens a browser tab at `http://localhost:8501`.

---

## ⚙️ Configuration

- Wikipedia is scraped for ticker lists and use **yfinance** for price data.  
- No external API key needed—just install the packages.

**Note**: To use the portfolio feature before the web-app is deployed, you will need to follow the steps below:

1. Create a `.streamlit` folder inside the `src` folder and place the `dummy_secrets.toml` there.
2. Fill in your own credentials and rename the file to `secrets.toml`. Make sure you add the ".streamlit" folder to the `.gitignore` file.
3. You will need an empty portfolio.db to get started. To make one, you need to explicitly run the `db_utils.py` script and it will generate a `portfolios.db` for you. 

First, navigate to the project folder and activate the environment.
```bash
cd live_stocks_tracker
conda activate live_stocks_tracker
```

After you activate your environment, you can run the code line below to generate the portfolios.db.

```bash
python -m src\live_stocks_tracker\utilities\db_utils
```


---

---

## 🤝 Contributing

1. Fork the repo  
2. Create a feature branch:  
   ```bash
   git checkout -b feature/YourFeature
   ```  
3. Commit your changes:  
   ```bash
   git commit -am "Add YourFeature"
   ```  
4. Push to your branch:  
   ```bash
   git push origin feature/YourFeature
   ```  
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.




