# 🪙 Binance Futures Order Bot

### 🚀 Overview
The **Binance Futures Order Bot** is a **CLI-based trading bot** built in **Python** that interacts with the **Binance USDT-M Futures Testnet**. It supports both **core trading orders** and **advanced automated strategies**, such as **TWAP** and **Grid Trading**, while maintaining strong **input validation**, **structured logging**, and **modular architecture**.



---

## 📂 Project Structure

```
[project_root]/
├── src/
│   ├── config.py              # API credentials and base URL
│   ├── binance_client.py      # Binance client initialization
│   ├── logger.py              # Logging utility
│   ├── validators.py          # Input validation functions
│   ├── market_orders.py       # Market order logic
│   ├── limit_orders.py        # Limit order logic
│   ├── cli.py                 # CLI for core order placement
│   ├── main_cli.py            # CLI for advanced order strategies
│   └── advanced/
│       ├── stop_limit.py      # Stop-Limit order logic
│       ├── oco.py             # OCO (One-Cancels-the-Other) order logic
│       ├── twap.py            # TWAP (Time-Weighted Average Price)
│       └── grid.py            # Grid Trading strategy
│
├── bot.log                    # Logs (API calls, errors, executions)
├── README.md                  # Setup, usage, and documentation
└── requirements.txt           # Python dependencies
```

---

## 🛠️ Setup Instructions

### 1️⃣ Prerequisites
- **Python 3.9+**
- **Binance Testnet account**
- **Binance Futures Testnet API key & secret**

---

### 2️⃣ Create and Activate Virtual Environment

#### On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### On Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

### 3️⃣ Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4️⃣ Set Up Binance Testnet API Keys

1. Go to the **Binance Futures Testnet**: [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Register or log in (Testnet uses a separate account)
3. Navigate to your profile → **API Management**
4. Click **Create API Key** → select **System generated**
5. Copy your:
   - **API Key**
   - **Secret Key**
6. Enable **Futures** and **Trade** permissions
7. Get free Test USDT funds from the Testnet Wallet

---

### 5️⃣ Configure API Keys

#### Option A – Direct Configuration (Simple, not for GitHub)
Edit `src/config.py`:

```python
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
```

#### Option B – Environment Variables (Recommended, safer)
Create a `.env` file in project root:

```ini
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

Update `src/config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
```

⚠️ Add `.env` to `.gitignore` before pushing to GitHub.

---

### 6️⃣ Verify Setup
Run:

```bash
python main.py
```

You should see output similar to:

```
Attempting to connect to Binance Futures Testnet...
Successfully retrieved account information.
--- Account Information ---
Can deposit: True
Can trade: True
Total wallet balance: 10000.0
Total unrealized PnL: 0.0
---------------------------
```

---

## 🧩 Core Features

### 1️⃣ Core Orders (Mandatory)

#### 🟢 Market Orders
Execute instantly at the current market price.

**Usage:**
```bash
python src/cli.py market_order --symbol BTCUSDT --side BUY --quantity 0.001
```

**How it works:**
- Validates inputs (symbol, side, quantity)
- Sends a MARKET order via Binance API
- Logs success/failure to `bot.log`

---

#### 🟠 Limit Orders
Execute when the market price reaches your specified limit price.

**Usage:**
```bash
python src/cli.py limit_order --symbol BTCUSDT --side SELL --quantity 0.001 --price 28000
```

**How it works:**
- Validates symbol, side, quantity, and price
- Sends a LIMIT order with `timeInForce='GTC'`
- Waits for execution and logs response

---

### 2️⃣ Advanced Orders (Bonus Features)

#### 🔵 Stop-Limit Orders
Trigger a limit order once a certain stop price is reached (useful for stop-loss or take-profit automation).

**Usage:**
```bash
python src/cli.py stop_limit_order --symbol BTCUSDT --side SELL --quantity 0.001 --price 28000 --stop_price 28100
```

**How it works:**
- Validates both `price` and `stop_price`
- Places a conditional STOP or TAKE_PROFIT order
- Automatically submits the limit order once stop triggers

---

#### 🔴 OCO (One-Cancels-the-Other) Orders
Place two linked orders (e.g., stop-loss and take-profit). When one executes, the other is automatically canceled.

**Usage:**
```bash
python src/cli.py oco_order --symbol BTCUSDT --side SELL --quantity 0.001 --price 28000 --stop_price 28100
```

**How it works:**
- Combines two orders under one OCO structure
- Automatically manages cancellation logic
- Ideal for automated risk management

---

#### 🟣 TWAP (Time-Weighted Average Price)
Splits a large order into multiple smaller orders executed at regular intervals to minimize price impact.

**Usage:**
```bash
python src/main_cli.py
# Choose option 4 (TWAP)
```

**Example Inputs:**
```
Symbol: BTCUSDT
Side: BUY
Total Quantity: 0.005
Number of Chunks: 5
Interval Seconds: 5
```

**How it works:**
- Divides total quantity into equal chunks
- Places MARKET orders one by one with a delay
- Logs every chunk execution with timestamps
- Produces a near-average market fill price

---

#### 🟡 Grid Trading
Places multiple buy/sell limit orders across a defined price range to profit from volatility.

**Usage:**
```bash
python src/main_cli.py
# Choose option 5 (Grid Trading)
```

**Example Inputs:**
```
Symbol: BTCUSDT
Quantity per Grid: 0.001
Lower Bound: 24000
Upper Bound: 26000
Number of Grids: 4
Monitor Interval: 60
```

**How it works:**
- Creates evenly spaced buy/sell limit orders between lower & upper price bounds
- Continuously monitors orders:
  - If a buy order fills → places a new sell higher
  - If a sell fills → places a new buy lower
- Runs until stopped manually (Ctrl+C)
- Logs all fills and replacements

---

## 🧮 Validation & Logging

### ✅ Input Validation
Implemented in `src/validators.py`:

- `validate_symbol(symbol)` – ensures proper symbol format (BTCUSDT)
- `validate_side(side)` – only BUY or SELL
- `validate_quantity(quantity)` – must be positive float
- `validate_price(price)` – must be positive float

All validations are enforced before any API request to prevent invalid trades.

---

### 📜 Logging
Implemented in `src/logger.py` using Python's built-in logging module.

**Features:**
- `bot.log` records:
  - Time, Level, Module, and Message
  - All order placements, responses, and errors
- Console shows INFO messages only (for clean output)
- File logs DEBUG and ERROR messages (for detailed debugging)

**Sample log entry:**
```
2025-11-07 03:42:15,210 | INFO | market_orders | Placed BUY MARKET order BTCUSDT qty=0.001 orderId=123456
2025-11-07 03:42:15,411 | ERROR | limit_orders | Invalid price provided: -5000
```

---

## 🧪 Testing & Reproducibility

### 1. Validate API connection:
```bash
python main.py
```

### 2. Test core market order:
```bash
python src/cli.py market_order --symbol BTCUSDT --side BUY --quantity 0.001
```

### 3. Check logs:
```bash
cat bot.log
```

### 4. Run advanced strategies:
```bash
python src/main_cli.py
```

Then choose:
- **4** for TWAP
- **5** for Grid Trading

---

## 📊 Example Outputs

### Console (TWAP)
```
Placing TWAP chunk 1 of 5...
Placing TWAP chunk 2 of 5...
...
TWAP execution finished for symbol=BTCUSDT
```

### Console (Grid)
```
Starting Grid Trading for BTCUSDT between 24000–26000
Placed BUY LIMIT order at 24100
Placed SELL LIMIT order at 25900
Monitoring fills every 60 seconds...
```

---







This is an educational project. Contributions, issues, and feature requests are welcome!

---

## 📧 Contact

For questions or feedback, please open an issue in the repository.
