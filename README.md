# Maritime Oil Trading P&L Analysis System

A professional Streamlit application for analyzing profit & loss in maritime oil trading operations.

## Features

🚢 **Cargo Management**: Track vessel information and trading operations  
📦 **Physical Trading**: Record oil purchase and sale transactions  
🛡️ **Futures Hedging**: Manage futures contracts for risk mitigation  
📊 **P&L Analysis**: Real-time profit & loss calculations  
📱 **Mobile Responsive**: Works on desktop and mobile devices  
📈 **Visualization**: Interactive charts and graphs  

## Quick Start

1. **Install Dependencies**
```bash
pip install streamlit pandas numpy plotly openpyxl
```

2. **Run Application**
```bash
python -m streamlit run app.py
```

3. **Access Application**
Open your browser to: http://localhost:8501

## Usage

### Load Sample Data
Click "📊 Load Sample Data" in the sidebar to populate with the GO-KAKI STAR example.

### Trading Operations Workflow
1. Go to "💼 Trading Operations" tab

#### Buy Operations
1. Select "🟢 Buy Operations" sub-tab
2. View current pending operations and open hedge positions
3. Click "➕ Add Buy Operation"
4. Enter physical oil purchase details (date, quantity, buy price)
5. Optionally add simultaneous hedge position entry (expiry defaults to purchase date)
6. Save to create pending operation
7. Monitor hedge ratio and operations summary

#### Sell Operations  
1. Select "🔴 Sell Operations" sub-tab
2. Click "➕ Add Sell Operation" 
3. Select pending buy operation to complete
4. Enter sale price and date
5. **Hedge Exit Feature**: Select hedge position to close from dropdown
   - When hedge is selected, "Hedge Exit Activated" menu appears automatically
   - Enter exit price for the selected hedge position
   - System validates that exit price is provided when hedge is selected
6. Complete the trading cycle with proper validation

### View Analysis
1. Go to "📊 P&L Analysis" tab to see calculated results
2. Go to "📈 Visualization" tab for charts and trends
3. Go to "📋 Records View" tab for complete trade history

## Calculation Methods

- **Physical P&L** = (Sale Price - Buy Price) × Quantity
- **Hedge P&L** = (Exit Price - Entry Price) × Volume  
- **Net P&L** = Physical P&L + Hedge P&L

## Testing

Run regression tests to validate calculations:
```bash
python test_validation.py
```

## Key Benefits

✅ **Excel Compatible**: Calculations match original Excel functionality  
✅ **Professional UI**: Clean, business-ready interface  
✅ **Real-time Updates**: Instant calculations as you input data  
✅ **Multi-platform**: Works on Windows, Mac, and Linux  
✅ **No Installation**: Web-based, no complex setup required  
✅ **Robust Validation**: Enhanced hedge exit validation prevents data entry errors  

## Technical Details

- Built with Streamlit for rapid deployment
- Responsive CSS design for mobile compatibility  
- Professional color scheme (blue/white theme)
- Input validation and error handling
- Regression tested against Excel data

## File Structure

```
├── app.py                 # Main Streamlit application
├── test_validation.py     # Regression test suite
├── analyze_excel.py       # Excel analysis utilities
└── README.md             # This file
```

## Support

For issues or questions, check the calculation logic in `test_validation.py` or review the Excel analysis in `analyze_excel.py`.

---
*Maritime Oil Trading P&L Analysis System - Professional POC*