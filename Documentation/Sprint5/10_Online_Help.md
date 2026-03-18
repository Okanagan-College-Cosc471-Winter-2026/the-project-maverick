---
pdf_options:
  format: Letter
  margin: 22mm
  headerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#888;">MarketSight - Online Help</div>'
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

## Online Help Guide

**Prepared by:** Zane Tessmer

COSC 471 - Winter 2026 | Okanagan College

March 17, 2026

</div>

<div style="page-break-after: always;"></div>

# 1. Built-in API Documentation

MarketSight provides interactive API documentation automatically generated from the FastAPI backend.

## Swagger UI
- **URL:** `/docs` (e.g., `http://localhost:8000/docs`)
- **Features:** Interactive endpoint testing, request/response schemas, parameter descriptions
- **Usage:** Click any endpoint to expand it, fill in parameters, and click "Try it out" to execute

## ReDoc
- **URL:** `/redoc` (e.g., `http://localhost:8000/redoc`)
- **Features:** Clean, readable API reference with nested schema documentation
- **Usage:** Browse the sidebar to navigate between endpoint groups

## Available API Endpoints

| Group | Endpoint | Method | Description |
|---|---|---|---|
| **Health** | `/api/v1/utils/health-check/` | GET | System health check |
| **Market** | `/api/v1/market/stocks` | GET | List all tracked stocks |
| **Market** | `/api/v1/market/stocks/{symbol}` | GET | Get stock metadata |
| **Market** | `/api/v1/market/stocks/{symbol}/ohlc` | GET | Get OHLC price data |
| **Market** | `/api/v1/market/stocks/{symbol}/coverage` | GET | Get data coverage info |
| **Inference** | `/api/v1/inference/predict/{symbol}` | GET | Generate price prediction |
| **Training** | `/api/v1/training/start` | POST | Start a training job |
| **Training** | `/api/v1/training/status` | GET | Get training job status |
| **Training** | `/api/v1/training/logs` | GET | Stream training logs (SSE) |
| **Data** | `/api/v1/data/snapshots` | GET | List dataset snapshots |
| **Data** | `/api/v1/data/snapshots/build` | POST | Build a new snapshot |
| **Data** | `/api/v1/data/snapshots/{name}` | GET | Download a snapshot file |

<div style="page-break-after: always;"></div>

# 2. In-Application Help

## Dashboard Help
- **Summary Cards:** Hover over any card to see a tooltip explaining the metric
- **API Status:** Green indicator = system healthy. If not green, the backend may be down.

## Stocks Page Help
- **Search Box:** Type any part of a stock symbol or company name to filter. Results update as you type.
- **"By Sector" Tab:** Stocks are grouped by market sector for easier comparison.
- **Clicking a Symbol:** Blue stock symbols are clickable links that open the stock detail page.

## Stock Chart Help
- **Chart Type Toggle:** The bar chart icon shows candlestick view; the line icon shows a simple line chart.
- **Time Range Buttons:** 1D (1 day), 1W (1 week), 1M (1 month), ALL (all available data).
- **Prediction Overlay:** Toggle "Show Prediction" to see an orange dashed line showing where the model predicts the price will go.
- **Green/Red Candles:** Green = price went up that day. Red = price went down.

## Predictions Page Help
- **Stock Selector:** Choose a stock from the dropdown, then click "Predict" for a single forecast.
- **Predict All:** Click to generate predictions for every tracked stock at once.
- **Confidence Colors:** Green (>70%) = high confidence. Yellow (40-70%) = moderate. Red (<40%) = low confidence.
- **View Chart:** Click this button on any prediction card to see the prediction overlaid on the chart.

## Settings Help
- **My Profile:** Click "Edit" to modify your name or email, then "Save" to apply changes.
- **Password:** All three fields are required. New password must be at least 8 characters.
- **Delete Account:** This action is permanent and cannot be undone.

## Admin Help (Superusers Only)
- **Add User:** Click the + button. Email and password are required.
- **Edit User:** Click the three-dot menu on any row, then "Edit User."
- **Delete User:** Click the three-dot menu, then "Delete User." Confirm in the dialog.

<div style="page-break-after: always;"></div>

# 3. Error Messages and Solutions

| Error Message | Meaning | Solution |
|---|---|---|
| "Stock not found" | The requested symbol doesn't exist in the database | Check the symbol spelling, or browse the Stocks page for available symbols |
| "Not enough data for prediction" | Fewer than 150 OHLC bars available | Wait for more data to be ingested, or try a different stock |
| "Prediction service unavailable" | The ML model encountered an error | Try again in a few minutes; contact admin if it persists |
| "No stocks available" | The market data hasn't been loaded | Contact your administrator to run the data seeding pipeline |
| "API Status: Offline" | The backend server is not responding | Check that the backend Docker container is running |
| "Loading..." (stuck) | A request is taking longer than expected | Refresh the page; check network connection |

# 4. Keyboard Navigation

| Key | Action |
|---|---|
| **Tab** | Move focus to the next interactive element |
| **Shift+Tab** | Move focus to the previous interactive element |
| **Enter/Space** | Activate buttons, toggle switches, open dropdowns |
| **Escape** | Close dialogs and dropdown menus |
| **Arrow Keys** | Navigate within dropdown options |

# 5. Getting Additional Help

- **User's Manual:** See `Documentation/Sprint4/Users_Manual.pdf` for comprehensive user instructions
- **Installation Guide:** See `Documentation/Sprint5/12_Installation_Guide.pdf` for setup instructions
- **Server Setup:** See `docs_server_setup.md` in the project root for DRI server documentation
- **API Reference:** Access `/docs` when the backend is running for interactive endpoint testing
- **Bug Reports:** Create an issue on the GitHub repository with steps to reproduce
