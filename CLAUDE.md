# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Maritime Oil Trading P&L Analysis System** - a professional Streamlit web application that replicates Excel-based trading analysis functionality. The system tracks vessel-based oil trading operations, including physical trades and futures hedging, with real-time profit & loss calculations.

## Key Commands

### Running the Application
```bash
python -m streamlit run app.py
```
Access at: http://localhost:8501

### Testing
```bash
python test_validation.py
```
Runs regression tests validating calculations against original Excel data with tolerance for fees/commissions.

### Excel Analysis
```bash
python analyze_excel.py
```
Analyzes the original Excel calculation logic for debugging purposes.

### Dependencies
```bash
pip install streamlit pandas numpy plotly openpyxl
```

## Architecture Overview

### Core Components

**app.py** - Main Streamlit application with 4-tab architecture:
- **Physical Trading Tab**: Multi-record input for oil purchase/sale transactions
- **Futures Hedging Tab**: Contract management for risk mitigation 
- **P&L Analysis Tab**: Real-time calculations with professional metrics display
- **Visualization Tab**: Interactive charts and time series analysis

**Session State Management**: Uses `st.session_state` to persist:
- `physical_trades[]` - List of physical trading records
- `hedge_trades[]` - List of futures hedge positions
- Form visibility flags for dynamic UI

### Critical Business Logic

**P&L Calculation Engine** (`calculate_pnl()` function):
```python
# Physical P&L = (Sale Price - Buy Price) × Quantity
# Hedge P&L = (Exit Price - Entry Price) × Volume  
# Net P&L = Physical P&L + Hedge P&L
```

**Important**: The hedge P&L formula uses `(Exit Price - Entry Price)` NOT `(Entry Price - Exit Price)` - this matches Excel's logic for sell hedges (negative volumes).

### Data Structure

**Physical Trade Records**:
```python
{
    'date': 'YYYY-MM-DD',
    'quantity': float,  # MT
    'buy_price': float,  # $/BBL
    'sale_price': float  # $/BBL
}
```

**Hedge Trade Records**:
```python
{
    'contract': str,     # Contract type
    'volume': float,     # MT (negative = sell hedge)
    'entry_price': float, # $/BBL
    'exit_price': float,  # $/BBL
    'expiry': 'YYYY-MM-DD',
    'status': str        # 'Open' or 'Closed'
}
```

### UI/UX Design System

**Color Coding**:
- Yellow background (`#fffbeb`) with amber border - Input sections
- Blue background (`#eff6ff`) with blue border - Result sections  
- Green/Red text - Profit/Loss indicators
- Professional blue gradient header

**Responsive Design**: CSS media queries for mobile compatibility, using Streamlit columns for layout.

## Excel Integration Context

This system was built to **exactly replicate** an existing Excel workbook (`AL BARAA_GO_FO_P&L Sales Blending_poc.xlsb.xlsx`) for the "GO-KAKI STAR 0.5%" cargo analysis case. 

**Test Data Validation**: The regression test suite (`test_validation.py`) validates against known Excel outputs with ~2% tolerance to account for Excel's additional factors (commissions, fees, rounding differences).

**Sample Data**: The "Load Sample Data" feature populates the GO-KAKI STAR case study:
- Physical: 245,778 MT at $72.46 buy / $78.96 sale
- Hedge: -245,778 MT GASOIL 500PPM at $75.87 entry / $81.98 exit

## Development Notes

**Session State Management**: Always check for key existence before accessing `st.session_state` collections. The app initializes empty lists for trades/hedges.

**Form Handling**: Dynamic forms use session state flags (e.g., `show_physical_form`) to control visibility. Forms are submitted with unique keys to prevent conflicts.

**Calculation Updates**: Any changes to the P&L calculation logic MUST be validated against `test_validation.py` to ensure Excel compatibility.

**Mobile Responsiveness**: Use `st.columns()` for responsive layouts. The CSS includes mobile-specific styles with media queries.

**Data Persistence**: No backend database - all data exists in session state and is lost on page refresh. "Load Sample Data" button provides quick testing setup.

## Testing Strategy

The codebase includes comprehensive regression testing that validates:
1. **Core calculations** against Excel expected values
2. **Edge cases** (zero quantities, negative values, multiple trades)
3. **Formula accuracy** with tolerance for Excel discrepancies

Test failures indicate potential calculation logic errors that could affect business accuracy.

## Excel Reference

The original Excel file contains the reference implementation for all calculations. The `analyze_excel.py` utility helps debug discrepancies between Python and Excel results. The system maintains calculation compatibility while providing a modern web interface.