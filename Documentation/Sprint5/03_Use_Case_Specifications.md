---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Use Case Specifications</div>'
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
  displayHeaderFooter: true
stylesheet: https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css
body_class: markdown-body
css: |-
  body { font-size: 12px; line-height: 1.7; }
  h1 { color: #1a5276; border-bottom: 2px solid #2980b9; padding-bottom: 6px; }
  h2 { color: #1a5276; border-bottom: 1px solid #bdc3c7; padding-bottom: 4px; margin-top: 18px; }
  h3 { color: #2c3e50; margin-top: 12px; }
  table { font-size: 11px; width: 100%; border-collapse: collapse; }
  th { background-color: #2980b9; color: white; padding: 5px 8px; }
  td { padding: 4px 8px; border: 1px solid #ddd; }
  tr:nth-child(even) { background-color: #f4f8fb; }
  .cover { text-align: center; margin-top: 80px; }
  .cover h1 { font-size: 32px; border: none; }
  .cover h2 { font-size: 16px; border: none; color: #7f8c8d; font-weight: 400; }
  .cover .line { border-top: 3px solid #2980b9; width: 100px; margin: 20px auto; }
---

<div class="cover">

# MarketSight

## Stock Market Prediction System

<div class="line"></div>

## Use Case Specifications

**Team:** Zane Tessmer, Harsh Kumar, Dante Bertolutti, Parag Jindal, Kaval S, Guntash

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# Use Case Diagram

```
                         +------------------------------------+
                         |          MarketSight               |
                         +------------------------------------+
                         |                                    |
   +--------+           | [UC-01] Get Stock Prediction        |
   |  User  |---------->| [UC-02] View Stock Chart            |
   +--------+           | [UC-03] Browse Stock List           |
       |                | [UC-04] Batch Predict All Stocks    |
       |                | [UC-05] Manage Account Settings     |
       |                +------------------------------------+
       |
   +---------+          +------------------------------------+
   |  Admin  |--------->| [UC-06] Manage User Accounts       |
   +---------+          +------------------------------------+
                                     |
   +---------+          +------------------------------------+
   |  Data   |--------->| [UC-07] Explore Data (Streamlit)   |
   | Analyst |          +------------------------------------+
   +---------+
```

<div style="page-break-after: always;"></div>

# UC-01: Get Stock Price Prediction

| Field | Description |
|---|---|
| **Use Case ID** | UC-01 |
| **Use Case Name** | Get Stock Price Prediction |
| **Primary Actor** | User |
| **XP Pair** | Dante Bertolutti & Harsh Kumar |
| **Description** | User selects a stock and receives an ML-generated price prediction with a confidence score |

## Flow of Events

### Main Flow
1. User navigates to the Predictions page (`/dashboard/predictions`)
2. System displays a stock selector dropdown populated with all active stocks
3. User selects a stock symbol (e.g., "AAPL - Apple Inc.")
4. User clicks the "Predict" button
5. System sends GET request to `/api/v1/inference/predict/{symbol}`
6. Backend validates that the stock exists in the database
7. Backend retrieves the most recent OHLC data (minimum 150 bars of 5-minute data)
8. Backend calculates 53 technical indicator features using the feature engineering module
9. Backend encodes the ticker symbol using the trained ticker encoder
10. XGBoost model generates a predicted return value
11. Backend calculates the predicted price from current price and predicted return
12. Backend calculates a confidence score (0.0-1.0) based on volatility, RSI, volume, and return magnitude
13. Backend returns a `PredictionResponse` JSON object
14. Frontend displays a prediction card showing: symbol, current price, predicted price, predicted return %, confidence score (color-coded), model version, and prediction date
15. User interprets the prediction and confidence score

### Alternative Flows
- **6a.** Stock not found: Backend returns 404. Frontend displays "Stock not found" error message.
- **7a.** Insufficient data (< 150 bars): Backend returns 400. Frontend displays "Not enough historical data for prediction."
- **8a.** Feature calculation error: Backend returns 500. Frontend displays "Prediction service unavailable."
- **10a.** Model not loaded: Backend returns 503. Frontend displays "Model is loading, please try again."

## Special Requirements
- Prediction inference must complete within 50ms
- Confidence score must be between 0.0 and 1.0
- Color coding: Green (> 0.7), Yellow (0.4-0.7), Red (< 0.4)
- Prediction card must show all fields from the PredictionResponse schema

## Pre-Conditions
- The backend server is running and healthy
- The XGBoost model is loaded in memory (native .ubj format)
- The stock exists in the database with at least 150 OHLC bars
- The ticker encoder is loaded from the model artifacts

## Post-Conditions
- User sees a prediction card with the predicted price, return, and confidence
- No database state is modified (read-only operation)

<div style="page-break-after: always;"></div>

# UC-02: View Stock Chart

| Field | Description |
|---|---|
| **Use Case ID** | UC-02 |
| **Use Case Name** | View Stock Chart |
| **Primary Actor** | User |
| **XP Pair** | Harsh Kumar & Parag Jindal |
| **Description** | User views an interactive OHLC chart for a stock with optional prediction overlay |

## Flow of Events

### Main Flow
1. User navigates to the Stocks page and clicks on a stock symbol
2. System navigates to `/dashboard/stocks/{symbol}`
3. System fetches stock metadata and OHLC data from the backend
4. System renders a candlestick chart using TradingView Lightweight Charts
5. Header displays: current price, price change (absolute + %), and latest volume
6. User can toggle between candlestick and line chart modes
7. User can select time range: 1D, 1W, 1M, or ALL
8. User toggles "Show Prediction" switch to ON
9. System sends a prediction request to the backend
10. System draws an orange dashed line from the last known price to the predicted price
11. Additional metrics appear: predicted price (60d), predicted return, confidence
12. User can switch to the Details tab to view stock metadata

### Alternative Flows
- **3a.** No OHLC data available: Chart area shows "No data available" placeholder
- **9a.** Prediction fails: Overlay is not drawn; chart continues to display OHLC data normally
- **7a.** 1D range with no intraday data: Chart appears empty; user should select 1W or longer

## Special Requirements
- Chart must be responsive (fills available width, 500px height)
- Range breaks must be applied to x-axis (skip weekends/holidays)
- Candlestick colors: Green for up days, Red for down days
- Prediction overlay: Orange dashed line

## Pre-Conditions
- Stock exists in the database with OHLC data
- Backend is running and serving the market API

## Post-Conditions
- User sees an interactive chart with the selected stock's price history
- If prediction overlay is enabled, predicted price is visualized on the chart

<div style="page-break-after: always;"></div>

# UC-03: Browse Stock List

| Field | Description |
|---|---|
| **Use Case ID** | UC-03 |
| **Use Case Name** | Browse Stock List |
| **Primary Actor** | User |
| **XP Pair** | Parag Jindal & Kaval S |
| **Description** | User browses and searches the list of tracked stocks |

## Flow of Events

### Main Flow
1. User navigates to `/dashboard/stocks`
2. System fetches the list of all active stocks from the backend
3. System displays stocks in a table: Symbol, Name, Sector, Exchange
4. User types in the search box to filter by symbol or company name
5. Results update in real-time as the user types
6. User switches to the "By Sector" tab to view stocks grouped by sector
7. User clicks on a stock symbol to navigate to the stock detail page

### Alternative Flows
- **2a.** No stocks loaded: System displays "No stocks available" with an explanation that data has not been loaded yet
- **4a.** Search returns no results: Filtered list is empty; search box remains active for editing

## Special Requirements
- Search must filter in real-time (no submit button)
- Stock symbols must be clickable links (blue, monospace font)
- Sector grouping must show collapsible sections

## Pre-Conditions
- Backend is running and the market API is available
- At least one stock exists in the database

## Post-Conditions
- User has found and can navigate to a stock of interest

<div style="page-break-after: always;"></div>

# UC-04: Batch Predict All Stocks

| Field | Description |
|---|---|
| **Use Case ID** | UC-04 |
| **Use Case Name** | Batch Predict All Stocks |
| **Primary Actor** | User |
| **XP Pair** | Dante Bertolutti & Harsh Kumar |
| **Description** | User generates predictions for all tracked stocks at once |

## Flow of Events

### Main Flow
1. User navigates to the Predictions page
2. User clicks the "Predict All" button
3. System sends prediction requests for all active stocks
4. System displays a loading spinner on the button during processing
5. Prediction cards appear in a responsive grid (3 columns on desktop, 2 on tablet, 1 on mobile)
6. Each card shows: symbol, predicted return badge (green up / red down), current price, predicted price, confidence %, model version
7. User can click "View Chart" on any card to navigate to that stock's detail page

### Alternative Flows
- **3a.** Some stocks fail prediction (insufficient data): Successful predictions display; failed stocks are skipped
- **3b.** Backend is unavailable: Error message displayed below the Predict All button

## Special Requirements
- All predictions must complete within 5 seconds for up to 10 stocks
- Grid layout must be responsive across screen sizes

## Pre-Conditions
- At least one stock exists with sufficient OHLC data
- Backend inference service is running with model loaded

## Post-Conditions
- User sees prediction cards for all successfully predicted stocks

<div style="page-break-after: always;"></div>

# UC-05: Manage Account Settings

| Field | Description |
|---|---|
| **Use Case ID** | UC-05 |
| **Use Case Name** | Manage Account Settings |
| **Primary Actor** | User |
| **XP Pair** | Kaval S & Guntash |
| **Description** | User views/edits profile, changes password, or deletes account |

## Flow of Events

### Main Flow (Profile Edit)
1. User navigates to `/dashboard/settings`
2. System displays the My Profile tab with current name and email
3. User clicks "Edit"
4. System enables input fields for Full Name and Email
5. User modifies fields and clicks "Save"
6. System sends update request to backend
7. System confirms the changes and returns to read-only view

### Alternative Flow (Change Password)
1. User switches to the Password tab
2. User enters current password, new password, and confirmation
3. User clicks "Update Password"
4. System validates: minimum 8 characters, passwords match
5. System updates the password and confirms success

### Alternative Flow (Delete Account)
1. User switches to the Danger Zone tab
2. User clicks "Delete Account"
3. System shows a confirmation dialog with warning
4. User clicks "Confirm Delete"
5. System permanently deletes the account and all associated data
6. User is redirected to the landing page

## Special Requirements
- Password fields must have show/hide toggle
- Delete account must require explicit confirmation
- Save button must be disabled when no changes are made

## Pre-Conditions
- User is logged in and has an active account

## Post-Conditions
- Profile changes are persisted, or account is deleted

<div style="page-break-after: always;"></div>

# UC-06: Manage User Accounts (Admin)

| Field | Description |
|---|---|
| **Use Case ID** | UC-06 |
| **Use Case Name** | Manage User Accounts |
| **Primary Actor** | Administrator (Superuser) |
| **XP Pair** | Parag Jindal & Guntash |
| **Description** | Admin adds, edits, or deletes user accounts |

## Flow of Events

### Main Flow (Add User)
1. Admin navigates to `/dashboard/admin`
2. System verifies superuser status (redirect to home if not superuser)
3. System displays the users table: Name, Email, Role, Status, Actions
4. Admin clicks "Add User" button
5. System opens a dialog with fields: Email, Full Name, Password, Confirm Password, Is Superuser, Is Active
6. Admin fills in required fields and clicks "Save"
7. System creates the new user and adds them to the table

### Alternative Flow (Edit User)
1. Admin clicks the three-dot menu on a user row
2. Admin selects "Edit User"
3. System opens a dialog pre-filled with the user's current information
4. Admin modifies fields (password fields are optional)
5. Admin clicks "Save"

### Alternative Flow (Delete User)
1. Admin clicks the three-dot menu on a user row
2. Admin selects "Delete User"
3. System shows confirmation dialog with warning about permanent deletion
4. Admin clicks "Delete" to confirm

## Special Requirements
- Only superusers can access the admin page
- Admin's own row must show a "You" badge
- Password fields: minimum 8 characters, must match

## Pre-Conditions
- User has superuser privileges

## Post-Conditions
- User account is created, modified, or deleted

<div style="page-break-after: always;"></div>

# UC-07: Explore Market Data (Streamlit)

| Field | Description |
|---|---|
| **Use Case ID** | UC-07 |
| **Use Case Name** | Explore Market Data via Streamlit |
| **Primary Actor** | Data Analyst |
| **XP Pair** | Harsh Kumar & Dante Bertolutti |
| **Description** | Analyst uses the Streamlit interface to browse data, run predictions, and manage datasets |

## Flow of Events

### Main Flow
1. Analyst opens the Streamlit application in their browser
2. System displays a sidebar with page navigation: Market Data, Inference, Datasets
3. Analyst selects "Market Data" to browse stocks and view OHLC data
4. Analyst selects "Inference" to run a prediction for a selected stock
5. Analyst selects "Datasets" to build, list, or download dataset snapshot files
6. Results are displayed interactively within the Streamlit interface

### Alternative Flows
- **2a.** Backend API unavailable: Streamlit shows a connection error with retry option
- **4a.** Prediction fails: Error message with reason displayed inline

## Special Requirements
- Streamlit app must connect to the same backend API as the React frontend
- Dataset downloads must be available as CSV/Parquet files

## Pre-Conditions
- Streamlit app is running
- Backend API is available and healthy

## Post-Conditions
- Analyst has explored data, run predictions, or downloaded datasets
