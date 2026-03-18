---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#999;">MarketSight User&#39;s Manual</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#999;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 11.5px; line-height: 1.65; color: #2c3e50; }
  h1 { color: #1a5276; border-bottom: 3px solid #2980b9; padding-bottom: 6px; font-size: 22px; }
  h2 { color: #1a5276; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 20px; font-size: 17px; }
  h3 { color: #2c3e50; margin-top: 14px; font-size: 14px; }
  h4 { color: #34495e; margin-top: 10px; font-size: 12px; }
  table { font-size: 10.5px; width: 100%; border-collapse: collapse; margin: 8px 0; }
  th { background-color: #2980b9; color: white; padding: 5px 8px; text-align: left; }
  td { padding: 4px 8px; border: 1px solid #ddd; }
  tr:nth-child(even) { background-color: #f4f8fb; }
  .cover { text-align: center; margin-top: 100px; }
  .cover h1 { font-size: 36px; border: none; color: #1a5276; margin-bottom: 0; }
  .cover h2 { font-size: 16px; border: none; color: #7f8c8d; font-weight: 400; margin-top: 6px; }
  .cover .divider { border-top: 3px solid #2980b9; width: 100px; margin: 24px auto; }
  .cover .subtitle { font-size: 20px; color: #2980b9; margin-top: 30px; font-weight: 600; }
  .cover .meta { color: #95a5a6; font-size: 12px; margin-top: 40px; line-height: 1.8; }
  blockquote { border-left: 4px solid #2980b9; background: #f4f8fb; padding: 10px 14px; margin: 10px 0; color: #34495e; }
  blockquote strong { color: #1a5276; }
  code { background: #eef3f7; padding: 1px 5px; border-radius: 3px; font-size: 10.5px; }
  .tip { border-left: 4px solid #27ae60; background: #f0faf4; padding: 10px 14px; margin: 10px 0; }
  .warning { border-left: 4px solid #e74c3c; background: #fdf2f2; padding: 10px 14px; margin: 10px 0; }
  .note { border-left: 4px solid #f39c12; background: #fef9e7; padding: 10px 14px; margin: 10px 0; }
---

<div class="cover">

# MarketSight

<h2>Stock Market Prediction System</h2>

<div class="divider"></div>

<div class="subtitle">User's Manual</div>

<div class="meta">

Version 1.0.0

March 3, 2026

COSC 471 - Winter 2026
Okanagan College

Prepared by: Zane Tessmer

</div>

</div>

<div style="page-break-after: always;"></div>

## Table of Contents

1. Introduction
2. Getting Started
3. Dashboard Overview
4. Browsing Stocks
5. Stock Details & Charts
6. Getting Predictions
7. Understanding Confidence Scores
8. Account Settings
9. Admin Panel (Superusers Only)
10. Appearance & Themes
11. Troubleshooting & FAQ
12. Glossary

<div style="page-break-after: always;"></div>

# 1. Introduction

### What is MarketSight?

MarketSight is a web-based stock market prediction platform that uses machine learning to forecast stock prices. The system analyzes historical market data and calculates technical indicators to generate predictions with confidence scores, helping you make more informed investment decisions.

### Who is this manual for?

This manual is written for **end users** of the MarketSight platform. No programming or technical background is required. Whether you are a retail investor, a finance student, or simply curious about stock market predictions, this guide will walk you through every feature of the application.

### Key Features at a Glance

| Feature | Description |
|---|---|
| **Stock Browser** | Search and browse stocks by name, symbol, or sector |
| **Interactive Charts** | View candlestick and line charts with adjustable time ranges |
| **ML Predictions** | Get AI-powered price forecasts for individual stocks or all at once |
| **Confidence Scores** | See how confident the model is in each prediction (color-coded) |
| **Prediction Overlay** | Visualize the predicted price directly on the stock chart |
| **User Settings** | Manage your profile, change your password, and control your account |
| **Admin Panel** | Manage user accounts (superusers only) |
| **Dark Mode** | Switch between light, dark, and system-matched themes |

<div style="page-break-after: always;"></div>

# 2. Getting Started

### Accessing MarketSight

Open your web browser and navigate to the MarketSight URL provided by your administrator. In a local development environment, this is typically:

> `http://localhost:5173`

### The Welcome Page

When you first visit MarketSight, you will see the **Welcome Page**. This page provides a brief overview of the platform's capabilities:

- **Historical Data** - Explore historical price data across multiple stocks
- **AI Predictions** - View data-driven forecasts powered by advanced ML models
- **Flexible Filtering** - Filter by date, exchange, and asset type

To begin using the application, click the **"Start exploring"** button. This will take you to the main Dashboard.

### Navigation

MarketSight uses a **sidebar navigation** on the left side of the screen. The sidebar contains links to all major sections:

| Menu Item | Icon | Description |
|---|---|---|
| **Dashboard** | Home | Your main overview page with summary statistics |
| **Stocks** | Chart | Browse, search, and view stock data and charts |
| **Predictions** | (via Stocks page) | Generate ML-powered price predictions |
| **Settings** | Gear | Manage your profile and account preferences |
| **Admin** | Users | Manage user accounts (visible to superusers only) |

You can **collapse the sidebar** by clicking the menu button in the top-left corner. This gives you more screen space for charts and data. Click it again to expand.

At the bottom of the sidebar, you will find:
- **Theme switcher** - Change between light, dark, and system themes
- **User menu** - View your profile info and log out

<div style="page-break-after: always;"></div>

# 3. Dashboard Overview

The Dashboard is your home screen. It gives you a quick snapshot of the system's current state through **four summary cards**:

### Summary Cards

| Card | What It Shows |
|---|---|
| **Total Stocks** | The number of stock symbols currently being tracked by MarketSight |
| **Sectors** | The number of unique market sectors represented (e.g., Technology, Healthcare) |
| **Model Version** | The current version of the ML model generating predictions |
| **API Status** | Whether the backend system is online and operational (green = healthy) |

These cards update automatically when the page loads. If the API Status shows anything other than "Online", the system may be experiencing issues - see the Troubleshooting section.

<div style="page-break-after: always;"></div>

# 4. Browsing Stocks

Navigate to the **Stocks** page by clicking "Stocks" in the sidebar.

### Searching for Stocks

At the top of the page, you will find a **search box**. Type any part of a stock's symbol or company name to instantly filter the list. For example:
- Typing `AAPL` will show Apple Inc.
- Typing `Tech` will show all stocks in technology-related sectors

The results update as you type - no need to press Enter.

### Viewing Modes

The Stocks page has two tabs:

**All Stocks** (default)
- Displays every stock in a single table
- Columns: Symbol, Name, Sector, Exchange
- Click any stock's **symbol** (shown in blue) to view its detail page

**By Sector**
- Groups stocks by their market sector (e.g., Technology, Healthcare, Energy)
- Each sector appears as a collapsible section
- Useful for comparing stocks within the same industry

### Stock Table Columns

| Column | Description |
|---|---|
| **Symbol** | The stock's ticker symbol (e.g., AAPL, MSFT). Click to view details. |
| **Name** | The full company name |
| **Sector** | The market sector the company belongs to. Shows "N/A" if not classified. |
| **Exchange** | The stock exchange where the stock is listed (e.g., NASDAQ, NYSE) |

> **Tip:** If you see "No stocks available", the market data has not been loaded yet. Contact your administrator.

<div style="page-break-after: always;"></div>

# 5. Stock Details & Charts

Click on any stock symbol from the Stocks page to open its **detail page**. This is where you can analyze historical price data and view ML predictions.

### Stock Header

At the top of the page, you will see:
- The **company name** and **ticker symbol**
- Badges showing the stock's **sector**, **industry**, and **exchange**
- A **back arrow** button to return to the Stocks list

### The Chart Tab

The Chart tab is selected by default and is the main feature of the stock detail page.

#### Price Information Bar

Above the chart, a row of key metrics is displayed:

| Metric | Description |
|---|---|
| **Current Price** | The most recent closing price in dollars |
| **Price Change** | How much the price changed from the previous day (in dollars and percent). Green = up, Red = down. |
| **Latest Volume** | The number of shares traded in the most recent session |

When the prediction overlay is enabled, additional metrics appear:

| Metric | Description |
|---|---|
| **Predicted Price (60d)** | The model's forecasted price. Green if higher than current, red if lower. |
| **Predicted Return** | The expected percentage change from current price to predicted price |
| **Confidence** | How confident the model is in this prediction (see Section 7) |

#### Chart Types

Two chart types are available. Toggle between them using the buttons in the top-right corner of the chart:

**Candlestick Chart**
- Each candle represents one trading day
- **Green candle** = the stock closed higher than it opened (bullish day)
- **Red candle** = the stock closed lower than it opened (bearish day)
- The thin lines (wicks) show the day's high and low prices
- Best for: Analyzing daily price action and trends

**Line Chart**
- Shows the closing price as a continuous blue line
- Simpler and cleaner view of the overall price trend
- Best for: Getting a quick sense of the stock's direction

#### Time Range Selection

Filter how much historical data is shown on the chart:

| Button | Range | Best For |
|---|---|---|
| **1D** | Last 1 day | Intraday detail |
| **1W** | Last 7 days | Short-term trend |
| **1M** | Last 30 days | Monthly overview |
| **ALL** | All available data | Long-term analysis |

#### Prediction Overlay

To see the ML prediction visualized on the chart:

1. Find the **"Show Prediction"** toggle switch in the control panel
2. Flip the switch to **ON**
3. The system will generate a prediction (you may see "Loading..." briefly)
4. An **orange dashed line** will appear on the chart, extending from the last known price to the predicted future price
5. The chart automatically zooms to the **1W** time range for the best view

> **Tip:** The prediction overlay is a great way to visually compare where the model thinks the price is headed versus recent price action.

### The Details Tab

Switch to the Details tab to see the stock's metadata in a card layout:
- Symbol, Name, Sector, Industry, and Exchange

<div style="page-break-after: always;"></div>

# 6. Getting Predictions

The **Predictions** page is your hub for generating and viewing ML-powered stock price forecasts. Navigate to it by clicking "Predictions" in the sidebar or through the Stocks page.

### Generating a Single Prediction

1. On the Predictions page, find the **"Generate Prediction"** card
2. Click the **stock selector dropdown** and choose a stock (e.g., "AAPL - Apple Inc.")
3. Click the **"Predict"** button
4. Wait a moment while the model generates the forecast (the button will show a loading spinner)
5. A **prediction card** will appear below with the results

### Predicting All Stocks at Once

If you want forecasts for every tracked stock:

1. Click the **"Predict All"** button (to the right of the Predict button)
2. The system will generate predictions for all active stocks
3. Multiple prediction cards will appear in a grid layout

### Reading a Prediction Card

Each prediction card contains:

| Field | Description |
|---|---|
| **Symbol** | The stock ticker (large, bold, top-left) |
| **Return Badge** | A colored badge showing the predicted return. Green with an up arrow for positive returns, red with a down arrow for negative returns. |
| **Prediction Date** | When this prediction was generated |
| **Current Price** | The stock's most recent closing price |
| **Predicted Price** | The model's forecasted price. Green text = price expected to go up, red = expected to go down. |
| **Confidence** | How reliable the model considers this prediction (shown as a percentage) |
| **Model Version** | Which version of the ML model was used |
| **View Chart** | Button to jump directly to the stock's chart with the prediction overlay |

### What to Do With Predictions

- **Compare** the predicted price against the current price to gauge expected movement
- **Check the confidence score** before acting on any prediction (see next section)
- **Click "View Chart"** to see the prediction in the context of recent price history
- **Use "Predict All"** to quickly scan for the strongest predicted movers across your tracked stocks

> **Note:** Predictions are forecasts, not guarantees. Always use predictions as one input among many in your decision-making process.

<div style="page-break-after: always;"></div>

# 7. Understanding Confidence Scores

Every prediction comes with a **confidence score** that tells you how reliable the model considers its forecast. This score ranges from 0% to 100%.

### How Confidence is Calculated

The confidence score is based on four market factors:

| Factor | What It Measures |
|---|---|
| **Volatility** | How much the stock's price has been fluctuating recently. Lower volatility = higher confidence. |
| **RSI (Relative Strength Index)** | Whether the stock is overbought or oversold. Extreme RSI values reduce confidence. |
| **Volume** | How actively the stock is being traded. Higher volume generally means more reliable predictions. |
| **Return Magnitude** | How large the predicted price change is. Very large predicted moves have lower confidence. |

### Color Coding

Confidence is displayed with intuitive color coding throughout the application:

| Color | Range | Meaning |
|---|---|---|
| **Green** | Above 70% | **High confidence.** The model is relatively sure about this prediction. Market conditions are stable and the predicted move is within normal range. |
| **Yellow** | 40% - 70% | **Moderate confidence.** Some uncertainty exists. The stock may be experiencing higher volatility or unusual trading patterns. |
| **Red** | Below 40% | **Low confidence.** The model is uncertain. This could be due to extreme market conditions, very low volume, or a large predicted move. Treat with caution. |

### How to Use Confidence Scores

- **High confidence (green):** The prediction is based on stable conditions. Consider it a stronger signal.
- **Moderate confidence (yellow):** Useful as a directional indicator, but verify with other analysis.
- **Low confidence (red):** The model is uncertain. Do not rely heavily on this prediction. Investigate why conditions may be unusual.

> **Important:** A high confidence score does NOT guarantee accuracy. It means the model's input conditions are favorable for making a prediction. Always combine ML predictions with your own research and analysis.

<div style="page-break-after: always;"></div>

# 8. Account Settings

Navigate to **Settings** in the sidebar to manage your account. The Settings page has three tabs.

### My Profile

View and edit your personal information.

**To view your profile:**
- Your full name and email are displayed on the page

**To edit your profile:**
1. Click the **"Edit"** button
2. Modify your **Full Name** or **Email** in the input fields
3. Click **"Save"** to apply changes, or **"Cancel"** to discard them

> The Save button is only clickable when you have actually changed something.

### Change Password

Update your account password.

1. Switch to the **Password** tab
2. Enter your **Current Password**
3. Enter your **New Password** (must be at least 8 characters)
4. Enter the new password again in the **Confirm Password** field
5. Click **"Update Password"**

Each password field has an **eye icon** you can click to temporarily show the password as you type.

> **Tip:** If you forget your current password, contact your administrator to reset it.

### Delete Account (Danger Zone)

Permanently remove your account and all associated data.

1. Switch to the **Danger Zone** tab
2. Click the red **"Delete Account"** button
3. A confirmation dialog will appear warning that all data will be permanently deleted
4. Click **"Confirm Delete"** to proceed, or **"Cancel"** to go back

> **Warning:** This action cannot be undone. All your account data will be permanently deleted.

<div style="page-break-after: always;"></div>

# 9. Admin Panel (Superusers Only)

The Admin page is only visible to users with **superuser** privileges. It allows you to manage all user accounts in the system.

Navigate to **Admin** in the sidebar.

### Viewing Users

The Admin page displays a table of all registered users:

| Column | Description |
|---|---|
| **Full Name** | The user's display name. Your own row is marked with a "You" badge. |
| **Email** | The user's email address |
| **Role** | Either "Superuser" (full admin access) or "User" (standard access) |
| **Status** | Green dot = Active, Gray dot = Inactive |
| **Actions** | Menu button for editing or deleting the user |

### Adding a New User

1. Click the **"Add User"** button (top-right, with a + icon)
2. Fill in the required fields:
   - **Email** (required) - must be a valid email address
   - **Full Name** (optional)
   - **Password** (required) - at least 8 characters
   - **Confirm Password** (required) - must match
3. Optionally check:
   - **Is superuser?** - gives the user admin access
   - **Is active?** - whether the account is enabled
4. Click **"Save"**

### Editing a User

1. Click the **three-dot menu** on the user's row
2. Select **"Edit User"**
3. Modify any fields as needed (password fields are optional - leave blank to keep the current password)
4. Click **"Save"**

### Deleting a User

1. Click the **three-dot menu** on the user's row
2. Select **"Delete User"**
3. A confirmation dialog will warn you that all associated data will be permanently deleted
4. Click **"Delete"** to confirm, or **"Cancel"** to go back

> **Warning:** Deleting a user is permanent and cannot be undone.

<div style="page-break-after: always;"></div>

# 10. Appearance & Themes

MarketSight supports three appearance modes so you can use the application comfortably in any lighting condition.

### Changing the Theme

1. Look at the **bottom of the sidebar**
2. Click the **theme switcher** dropdown
3. Select one of three options:

| Theme | Description |
|---|---|
| **Light** | White backgrounds with dark text. Best for well-lit environments. |
| **Dark** | Dark backgrounds with light text. Easier on the eyes in low-light conditions. |
| **System** | Automatically matches your operating system's theme setting. If your OS switches between light and dark mode, MarketSight will follow. |

Your theme preference is saved and will persist across browser sessions.

<div style="page-break-after: always;"></div>

# 11. Troubleshooting & FAQ

### Common Issues

**Q: The dashboard shows "Loading..." and never finishes.**
> The backend server may be down. Check that the API Status card shows "Online". If it doesn't, contact your system administrator to restart the backend services.

**Q: I see "No stocks available" on the Stocks page.**
> Market data has not been loaded into the system yet. An administrator needs to run the data seeding process, or the Airflow pipeline needs to complete its first run.

**Q: My prediction failed with an error message.**
> This can happen if:
> - The stock doesn't have enough historical data (at least 30 days of OHLC data is needed)
> - The ML model is not loaded on the backend
> - The backend server is temporarily unavailable
>
> Try again in a few minutes. If the problem persists, contact your administrator.

**Q: The prediction overlay isn't showing on the chart.**
> Make sure the "Show Prediction" toggle is switched ON. If it shows "Loading..." for an extended time, the prediction may have failed silently. Try toggling it off and on again.

**Q: I can't see the Admin page in the sidebar.**
> The Admin page is only visible to users with superuser privileges. If you need admin access, ask an existing superuser to upgrade your account.

**Q: I forgot my password.**
> Contact your system administrator or a superuser to reset your password through the Admin panel.

**Q: The chart looks empty or shows very few data points.**
> Try changing the time range. If you selected "1D" but there's no intraday data, the chart may appear empty. Switch to "1W", "1M", or "ALL" to see more data.

**Q: Can I export predictions or chart data?**
> This feature is not currently available in version 1.0.0. It is planned for a future release.

<div style="page-break-after: always;"></div>

# 12. Glossary

| Term | Definition |
|---|---|
| **OHLCV** | Open, High, Low, Close, Volume - the five standard data points recorded for each trading session |
| **Candlestick Chart** | A chart type where each bar shows the open, high, low, and close prices for a trading period. Green = price went up, Red = price went down. |
| **Line Chart** | A chart that connects closing prices with a continuous line, showing the overall trend |
| **RSI** | Relative Strength Index - a momentum indicator measuring the speed and magnitude of price changes. Values above 70 suggest overbought, below 30 suggest oversold. |
| **MACD** | Moving Average Convergence Divergence - a trend-following indicator that shows the relationship between two moving averages of a stock's price |
| **Bollinger Bands** | A volatility indicator consisting of a moving average with upper and lower bands set at standard deviations away |
| **XGBoost** | Extreme Gradient Boosting - the machine learning algorithm used by MarketSight to generate price predictions |
| **Confidence Score** | A value from 0% to 100% indicating how reliable the model considers its prediction, based on market conditions |
| **Prediction Overlay** | A visual element on the chart (orange dashed line) showing where the model predicts the price will go |
| **Ticker Symbol** | A short abbreviation used to identify a publicly traded stock (e.g., AAPL for Apple Inc.) |
| **Sector** | A broad category grouping companies by industry (e.g., Technology, Healthcare, Energy) |
| **Volume** | The number of shares traded during a given period. Higher volume indicates more market activity. |
| **Volatility** | A measure of how much a stock's price fluctuates. High volatility means larger price swings. |
| **Superuser** | An account with administrative privileges, including the ability to manage other user accounts |
| **Airflow** | An automated pipeline system that handles data loading and model retraining on a schedule |
| **Dashboard** | The main overview page showing summary statistics about the system |
| **MVP** | Minimum Viable Product - the first functional version of the software with core features |

---

<div style="text-align: center; margin-top: 40px; color: #95a5a6; font-size: 11px;">

**MarketSight User's Manual v1.0.0**

Prepared by Zane Tessmer | March 2026

COSC 471 - Okanagan College

</div>
