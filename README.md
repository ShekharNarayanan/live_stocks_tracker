# 📉📈 Live Stocks Tracker

A simple Streamlit web-app to scan US large-, mid- and small-cap universes for the **top losers & gainers** over a customizable look-back window. Powered by [yfinance](https://pypi.org/project/yfinance/) and Wikipedia scrapes—no paid API keys required.

---

## ✨ Features

- 🔎 **Universe selection**: S&P 500 (large), S&P 400 (mid), or S&P 600 (small)  
- ⏱️ **Custom look-back**: pick any period between 5 and 90 days  
- 📑 **Top 20 lists**: see your biggest losers & gainers side-by-side  
- 📊 **Key metrics**: % change, RSI-14, average 30-day volume  
- 🔄 **Auto-refresh**: results update instantly when you tweak sidebar controls  
- 🏃‍♂️ **One-click scan**: or auto-run on first page load  

---
<!---usage video --->
![usage][media/usage_gif.gif]



## 🚀 Getting Started

### 1. Clone this repo  
```bash
git clone https://github.com/ShekharNarayanan/live-stocks-tracker.git
cd live-stocks-tracker
```

### 2. Install dependencies  
Create and activate a virtual environment, then install:
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run the app  
```bash
streamlit run app.py
```
This opens a browser tab at `http://localhost:8501`.

---

## ⚙️ Configuration

- We scrape Wikipedia for ticker lists and use **yfinance** for price data.  
- No external API key needed—just install the packages.

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