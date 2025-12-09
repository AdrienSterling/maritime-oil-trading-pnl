import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import io
import json


# Page configuration

BASE_DIR = Path(__file__).resolve().parent

# Logo paths
LOGO_PATH = BASE_DIR / "logo.png"
FAVICON_PATH = BASE_DIR / "favicon.png"

PLATTS_PRODUCT_CATALOG = {
    'MOPAG': [
        '180 CST AG MOPAG',
        '380 CST AG MOPAG',
        'GASOIL 2500PPM MOPAG',
        'GASOIL 500PPM MOPAG',
        'GASOIL 10PPM MOPAG',
        'NAPHTHA MOPAG'
    ],
    'MOPS': [
        '180 CST SPOR MOPS',
        '380 CST SPOR MOPS',
        'GAS OIL2500PPM MOPS',
        'GASOIL 500PPM MOPS',
        'GASOIL 10PPM MOPS',
        'GASOLINE 92 MOPS',
        'GASOLINE 95 MOPS'
    ]
}


# Page configuration
st.set_page_config(
    page_title="Oil Trading P&L Analysis",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - Light Professional Business Theme
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #ffffff;
    }

    /* Light Professional Header */
    .main-header {
        background: #ffffff;
        padding: 1.25rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .header-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        max-width: 1400px;
        margin: 0 auto;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .header-divider {
        width: 1px;
        height: 40px;
        background: #e5e7eb;
        margin: 0 16px;
    }

    .header-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.3px;
    }

    .header-subtitle {
        color: #6b7280;
        font-size: 0.8rem;
        font-weight: 400;
        margin: 4px 0 0 0;
    }

    /* Main Content Area */
    .block-container {
        padding-top: 1rem;
    }

    /* Input Section */
    .input-section {
        background: #fafafa;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Result Section */
    .result-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    /* Professional Metric Cards */
    .metric-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        text-align: center;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }

    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #d1d5db;
    }

    .metric-card h3 {
        color: #111827;
        margin: 0.5rem 0;
        font-size: 1.6rem;
        font-weight: 600;
    }

    .metric-card h4 {
        color: #6b7280;
        margin: 0;
        font-weight: 500;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-card p {
        color: #9ca3af;
        font-size: 0.75rem;
        margin: 0.25rem 0 0 0;
    }

    /* P&L Colors */
    .profit-positive {
        color: #059669 !important;
        font-weight: 700;
    }

    .profit-negative {
        color: #dc2626 !important;
        font-weight: 700;
    }

    /* Section Headers in markdown */
    .stMarkdown h3 {
        color: #374151;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e7eb;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #fafafa;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #374151;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        border-bottom: none;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: transparent;
        padding: 0;
        border-bottom: 1px solid #e5e7eb;
        border-radius: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        color: #6b7280;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.75rem 1.25rem;
        border-bottom: 2px solid transparent;
        margin-bottom: -1px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #374151;
    }

    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #4a9d4e !important;
        border-bottom: 2px solid #4a9d4e !important;
        box-shadow: none;
    }

    /* Button Styling */
    .stButton > button {
        background: #ffffff;
        border: 1px solid #d1d5db;
        color: #374151;
        font-weight: 500;
        font-size: 0.875rem;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }

    .stButton > button:active {
        background: #f3f4f6;
    }

    /* Primary Button - Green accent */
    .stButton > button[kind="primary"] {
        background: #4a9d4e;
        border: 1px solid #4a9d4e;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #3d8b40;
        border-color: #3d8b40;
    }

    /* Form inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 6px;
        border: 1px solid #d1d5db;
        font-size: 0.875rem;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #4a9d4e;
        box-shadow: 0 0 0 1px #4a9d4e;
    }

    /* DataFrames */
    .stDataFrame {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] > div {
        border-radius: 8px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #fafafa;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
    }

    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 6px;
        font-size: 0.875rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        color: #6b7280;
        font-size: 0.8rem;
        border-top: 1px solid #e5e7eb;
        margin-top: 3rem;
        background: #fafafa;
    }

    .footer a {
        color: #4a9d4e;
        text-decoration: none;
        font-weight: 500;
    }

    .footer a:hover {
        text-decoration: underline;
    }

    /* Metrics styling */
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }

    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }

        .header-container {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
        }

        .header-divider {
            display: none;
        }

        .header-title {
            font-size: 1.25rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main header with logo
import base64

def get_base64_image(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

logo_base64 = get_base64_image(LOGO_PATH) if LOGO_PATH.exists() else None

header_html = """
<div class="main-header">
    <div class="header-container">
        <div class="header-left">
            <div>
                <h1 class="header-title">Oil Trading P&L Analysis</h1>
                <p class="header-subtitle">Professional Risk Management & Trading Analytics Platform</p>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# Calculation functions
def calculate_pnl(physical_trades, hedge_trades):
    """Calculate P&L"""
    # Physical trading P&L
    physical_pnl = 0
    for trade in physical_trades:
        quantity = trade.get('quantity', 0)
        if quantity != 0:
            sale_price_base = trade.get('sale_price', 0.0)
            sale_premium = trade.get('sale_premium_discount', 0.0)
            if sale_price_base <= 0 and sale_premium == 0:
                continue
            buy_price = trade.get('buy_price', 0.0) + trade.get('buy_premium_discount', 0.0)
            sale_price = sale_price_base + sale_premium
            pnl = (sale_price - buy_price) * quantity
            physical_pnl += pnl
    
    # Hedge P&L
    hedge_pnl = 0
    for hedge in hedge_trades:
        if hedge['volume'] != 0:
            pnl = (hedge['exit_price'] - hedge['entry_price']) * hedge['volume']
            hedge_pnl += pnl
    
    # Net P&L
    net_pnl = physical_pnl + hedge_pnl
    
    return physical_pnl, hedge_pnl, net_pnl



def standardize_market_price_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['date', 'instrument', 'price', 'type'])

    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    column_map = {
        'date': ['date', 'valuation_date', 'pricing_date'],
        'instrument': ['instrument', 'product', 'contract', 'name'],
        'price': ['price', 'market_price', 'settlement', 'value'],
        'type': ['type', 'category', 'instrument_type']
    }

    resolved = {}
    for canonical, aliases in column_map.items():
        for alias in aliases:
            if alias in df.columns:
                resolved[canonical] = alias
                break

    missing_required = [key for key in ['date', 'instrument', 'price'] if key not in resolved]
    if missing_required:
        raise ValueError(f"Missing required columns: {', '.join(missing_required)}")

    rename_map = {resolved['date']: 'date', resolved['instrument']: 'instrument', resolved['price']: 'price'}
    if 'type' in resolved:
        rename_map[resolved['type']] = 'type'

    df = df.rename(columns=rename_map)
    if 'type' not in df.columns:
        df['type'] = ''
    return df[['date', 'instrument', 'price', 'type']]


def normalize_market_price_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['date', 'instrument', 'price', 'type', 'instrument_key'])

    df = standardize_market_price_columns(df)
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    df['instrument'] = df['instrument'].astype(str).str.strip()
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['type'] = df['type'].fillna('').astype(str).str.strip()
    df = df.dropna(subset=['date', 'instrument'])
    df = df[df['instrument'] != '']
    df = df.dropna(subset=['price'])
    df['instrument_key'] = df['instrument'].str.lower().str.strip()
    df = df.sort_values(['date', 'instrument_key']).reset_index(drop=True)
    return df


def get_market_price_df() -> pd.DataFrame:
    data = st.session_state.get('market_prices', [])
    if isinstance(data, pd.DataFrame):
        df = normalize_market_price_df(data)
    else:
        df = normalize_market_price_df(pd.DataFrame(data))
    return df


def save_market_price_df(df: pd.DataFrame) -> None:
    normalized = normalize_market_price_df(df)
    if normalized.empty:
        st.session_state.market_prices = []
        return

    to_store = normalized.drop(columns=['instrument_key'])
    to_store['date'] = to_store['date'].dt.strftime('%Y-%m-%d')
    st.session_state.market_prices = to_store.to_dict(orient='records')


def lookup_market_price(prices_df: pd.DataFrame, instrument_name: str, valuation_date: pd.Timestamp):
    if prices_df.empty or not instrument_name:
        return None

    key = str(instrument_name).strip().lower()
    if not key:
        return None

    valuation_date = pd.to_datetime(valuation_date).normalize()
    subset = prices_df[(prices_df['instrument_key'] == key) & (prices_df['date'] == valuation_date)]
    if subset.empty:
        return None
    return subset.iloc[-1]['price']


def evaluate_market_pnl_for_date(prices_df: pd.DataFrame, physical_trades, hedge_trades, valuation_date):
    valuation_date = pd.to_datetime(valuation_date).normalize()

    physical_rows = []
    hedge_rows = []
    physical_pnl = 0.0
    hedge_pnl = 0.0
    missing_instruments = set()

    for idx, trade in enumerate(physical_trades, start=1):
        quantity = trade.get('quantity', 0) or 0
        if quantity == 0:
            continue

        buy_date = trade.get('date')
        if buy_date:
            try:
                buy_date = pd.to_datetime(buy_date).normalize()
                if buy_date > valuation_date:
                    continue
            except Exception:
                buy_date = None

        sale_date = trade.get('sale_date') or ''
        if sale_date:
            try:
                sale_date = pd.to_datetime(sale_date).normalize()
            except Exception:
                sale_date = None
        else:
            sale_date = None

        status = 'Open'
        if sale_date and sale_date <= valuation_date:
            status = 'Closed'

        product_name = trade.get('product_name') or trade.get('product') or st.session_state.get('selected_product_name', '')
        net_buy_price = (trade.get('buy_price', 0.0) or 0.0) + (trade.get('buy_premium_discount', 0.0) or 0.0)
        market_price = lookup_market_price(prices_df, product_name, valuation_date)
        pnl_value = np.nan

        if status == 'Open':
            if market_price is not None:
                pnl_value = (market_price - net_buy_price) * quantity
                physical_pnl += pnl_value
            else:
                missing_instruments.add(product_name or 'Physical Product')
        else:
            pnl_value = 0.0

        physical_rows.append({
            'Trade #': idx,
            'Instrument': product_name or 'N/A',
            'Status': status,
            'Quantity (MT)': quantity,
            'Net Buy Price ($/BBL)': net_buy_price,
            'Market Price ($/BBL)': market_price,
            'P&L ($)': pnl_value
        })

    for idx, hedge in enumerate(hedge_trades, start=1):
        volume = hedge.get('volume', 0) or 0
        if volume == 0:
            continue

        trade_date = hedge.get('trade_date')
        if trade_date:
            try:
                trade_date = pd.to_datetime(trade_date).normalize()
                if trade_date > valuation_date:
                    continue
            except Exception:
                trade_date = None

        exit_date = hedge.get('exit_date') or ''
        if exit_date:
            try:
                exit_date = pd.to_datetime(exit_date).normalize()
            except Exception:
                exit_date = None
        else:
            exit_date = None

        status = hedge.get('status', 'Open')
        if exit_date and exit_date <= valuation_date:
            status = 'Closed'

        contract_name = hedge.get('contract') or 'Hedge Instrument'
        entry_price = hedge.get('entry_price', 0.0) or 0.0
        market_price = lookup_market_price(prices_df, contract_name, valuation_date)
        pnl_value = np.nan

        if status == 'Open':
            if market_price is not None:
                pnl_value = (market_price - entry_price) * volume
                hedge_pnl += pnl_value
            else:
                missing_instruments.add(contract_name)
        else:
            pnl_value = 0.0

        hedge_rows.append({
            'Hedge #': idx,
            'Instrument': contract_name,
            'Status': status,
            'Volume': volume,
            'Entry Price ($/BBL)': entry_price,
            'Market Price ($/BBL)': market_price,
            'P&L ($)': pnl_value
        })

    physical_df = pd.DataFrame(physical_rows) if physical_rows else pd.DataFrame(columns=['Trade #', 'Instrument', 'Status', 'Quantity (MT)', 'Net Buy Price ($/BBL)', 'Market Price ($/BBL)', 'P&L ($)'])
    hedge_df = pd.DataFrame(hedge_rows) if hedge_rows else pd.DataFrame(columns=['Hedge #', 'Instrument', 'Status', 'Volume', 'Entry Price ($/BBL)', 'Market Price ($/BBL)', 'P&L ($)'])

    return {
        'valuation_date': valuation_date,
        'physical_pnl': float(physical_pnl),
        'hedge_pnl': float(hedge_pnl),
        'net_pnl': float(physical_pnl + hedge_pnl),
        'physical_details': physical_df,
        'hedge_details': hedge_df,
        'missing_instruments': sorted({m for m in missing_instruments if m})
    }


def calculate_market_pnl_series(prices_df: pd.DataFrame, physical_trades, hedge_trades) -> pd.DataFrame:
    if prices_df.empty:
        return pd.DataFrame(columns=['date', 'physical_pnl', 'hedge_pnl', 'net_pnl'])

    results = []
    for valuation_date in sorted(prices_df['date'].dropna().unique()):
        pnl_snapshot = evaluate_market_pnl_for_date(prices_df, physical_trades, hedge_trades, valuation_date)
        results.append({
            'date': pd.to_datetime(valuation_date),
            'physical_pnl': pnl_snapshot['physical_pnl'],
            'hedge_pnl': pnl_snapshot['hedge_pnl'],
            'net_pnl': pnl_snapshot['net_pnl']
        })

    return pd.DataFrame(results)


def build_price_history(prices_df: pd.DataFrame, instruments) -> pd.DataFrame:
    if prices_df.empty or not instruments:
        return pd.DataFrame()

    instrument_keys = {str(instr).strip().lower() for instr in instruments if instr}
    if not instrument_keys:
        return pd.DataFrame()

    subset = prices_df[prices_df['instrument_key'].isin(instrument_keys)]
    if subset.empty:
        return pd.DataFrame()

    pivot = (subset.pivot_table(index='date', columns='instrument', values='price', aggfunc='last')
                    .sort_index())
    pivot = pivot.reset_index()
    return pivot






# Initialize session state
if 'physical_trades' not in st.session_state:
    st.session_state.physical_trades = []
if 'hedge_trades' not in st.session_state:
    st.session_state.hedge_trades = []

for trade in st.session_state.physical_trades:
    trade.setdefault('buy_premium_discount', 0.0)
    trade.setdefault('sale_premium_discount', 0.0)
    trade.setdefault('sale_date', '')
    trade.setdefault('product_name', st.session_state.get('selected_product_name', ''))
    trade.setdefault('product_category', st.session_state.get('selected_product_category', ''))

for hedge in st.session_state.hedge_trades:
    hedge.setdefault('exit_date', '')

if 'market_prices' not in st.session_state:
    st.session_state.market_prices = []

if 'selected_product_category' not in st.session_state:
    st.session_state.selected_product_category = ''
if 'selected_product_name' not in st.session_state:
    st.session_state.selected_product_name = ''

# Sidebar - Basic Information
with st.sidebar:
    st.markdown("### Cargo Information")

    cargo_name = st.text_input(
        "Cargo Name",
        value="GO-KAKI STAR 0.5%",
        help="Enter vessel name"
    )

    delivery_point = st.text_input(
        "Delivery Point",
        value=st.session_state.get("delivery_point", ""),
        help="Enter the delivery or discharge location"
    )
    st.session_state.delivery_point = delivery_point


    product_catalog = {category: items[:] for category, items in PLATTS_PRODUCT_CATALOG.items()}
    categories = sorted(product_catalog.keys())
    previous_category = st.session_state.get("selected_product_category")

    if categories:
        if previous_category not in categories:
            previous_category = categories[0]
        category_index = categories.index(previous_category) if previous_category else 0
        product_category = st.selectbox(
            "Product Category",
            categories,
            index=category_index,
            help="Select the market pricing family (e.g. MOPAG or MOPS)"
        )
        st.session_state.selected_product_category = product_category

        products = product_catalog.get(product_category, [])
        previously_selected = st.session_state.get("selected_product_name", "")

        if products:
            default_index = products.index(previously_selected) if previously_selected in products else 0
            product_selection = st.selectbox(
                "Product",
                products,
                index=default_index,
                help="Choose the product under the selected category"
            )
        else:
            product_selection = st.text_input(
                "Product",
                value=previously_selected,
                help="Enter product name (no predefined products for this category)"
            )
    else:
        manual_category = st.text_input(
            "Product Category",
            value=st.session_state.get("selected_product_category", ""),
            help="Enter a product category"
        )
        st.session_state.selected_product_category = manual_category
        product_selection = st.text_input(
            "Product",
            value=st.session_state.get("selected_product_name", ""),
            help="Enter product name"
        )

    if product_selection:
        st.session_state.selected_product_name = product_selection
    else:
        st.session_state.selected_product_name = st.session_state.get("selected_product_name", "Custom Product")

    product_name = st.session_state.selected_product_name

    col1, col2 = st.columns(2)


    with col1:
        purchase_start = st.date_input(
            "Purchase Start Date",
            value=date(2019, 1, 1)
        )
    with col2:
        purchase_end = st.date_input(
            "Purchase End Date", 
            value=date(2019, 2, 7)
        )
    
    date_range_valid = purchase_start <= purchase_end
    if not date_range_valid:
        st.warning("Purchase end date must be on or after start date.")

    st.markdown("---")
    st.markdown("### Quick Actions")

    if st.button("Reset All Data"):
        st.session_state.physical_trades = []
        st.session_state.hedge_trades = []
        st.session_state.market_prices = []
        st.rerun()

    # Demo data presets
    st.markdown("**Load Demo Data:**")
    demo_preset = st.selectbox(
        "Select Demo Scenario",
        ["-- Select --", "GO-KAKI STAR (Completed)", "FO Cargo (Open Position)", "Multi-Trade Portfolio"],
        key="demo_preset_selector",
        label_visibility="collapsed"
    )

    if st.button("Load Selected Demo"):
        if demo_preset == "GO-KAKI STAR (Completed)":
            st.session_state.physical_trades = [{
                'date': '2019-01-15',
                'quantity': 245778,
                'buy_price': 72.46,
                'buy_premium_discount': 0.0,
                'sale_price': 78.96,
                'sale_premium_discount': 0.0,
                'sale_date': '2019-02-01',
                'product_name': '180 CST AG MOPAG',
                'product_category': 'MOPAG'
            }]
            st.session_state.hedge_trades = [{
                'contract': 'GASOIL Mo1',
                'volume': -245778,
                'entry_price': 75.87,
                'exit_price': 81.98,
                'trade_date': '2019-01-15',
                'status': 'Closed',
                'exit_date': '2019-02-01'
            }]
            st.rerun()
        elif demo_preset == "FO Cargo (Open Position)":
            st.session_state.physical_trades = [{
                'date': '2024-03-01',
                'quantity': 150000,
                'buy_price': 68.50,
                'buy_premium_discount': -1.25,
                'sale_price': 0.0,
                'sale_premium_discount': 0.0,
                'sale_date': '',
                'product_name': '380 CST AG MOPAG',
                'product_category': 'MOPAG'
            }]
            st.session_state.hedge_trades = [{
                'contract': 'GASOIL Mo2',
                'volume': -150000,
                'entry_price': 71.20,
                'exit_price': 0.0,
                'trade_date': '2024-03-01',
                'status': 'Open',
                'exit_date': ''
            }]
            st.rerun()
        elif demo_preset == "Multi-Trade Portfolio":
            st.session_state.physical_trades = [
                {
                    'date': '2024-01-10',
                    'quantity': 100000,
                    'buy_price': 70.00,
                    'buy_premium_discount': 0.50,
                    'sale_price': 74.50,
                    'sale_premium_discount': 0.25,
                    'sale_date': '2024-01-25',
                    'product_name': 'GASOIL 500PPM MOPAG',
                    'product_category': 'MOPAG'
                },
                {
                    'date': '2024-02-01',
                    'quantity': 200000,
                    'buy_price': 72.00,
                    'buy_premium_discount': -0.50,
                    'sale_price': 75.00,
                    'sale_premium_discount': 0.0,
                    'sale_date': '2024-02-15',
                    'product_name': 'GASOIL 500PPM MOPAG',
                    'product_category': 'MOPAG'
                },
                {
                    'date': '2024-02-20',
                    'quantity': 180000,
                    'buy_price': 69.00,
                    'buy_premium_discount': 0.0,
                    'sale_price': 0.0,
                    'sale_premium_discount': 0.0,
                    'sale_date': '',
                    'product_name': '180 CST AG MOPAG',
                    'product_category': 'MOPAG'
                }
            ]
            st.session_state.hedge_trades = [
                {
                    'contract': 'GASOIL Mo1',
                    'volume': -100000,
                    'entry_price': 72.50,
                    'exit_price': 76.00,
                    'trade_date': '2024-01-10',
                    'status': 'Closed',
                    'exit_date': '2024-01-25'
                },
                {
                    'contract': 'GASOIL Mo1',
                    'volume': -200000,
                    'entry_price': 74.00,
                    'exit_price': 77.50,
                    'trade_date': '2024-02-01',
                    'status': 'Closed',
                    'exit_date': '2024-02-15'
                },
                {
                    'contract': 'GASOIL Mo2',
                    'volume': -180000,
                    'entry_price': 71.00,
                    'exit_price': 0.0,
                    'trade_date': '2024-02-20',
                    'status': 'Open',
                    'exit_date': ''
                }
            ]
            st.rerun()
        else:
            st.warning("Please select a demo scenario first.")

    st.markdown("---")
    st.markdown("### Data Import/Export")

    # Export to Excel
    if st.session_state.physical_trades or st.session_state.hedge_trades or st.session_state.market_prices:
        export_buffer = io.BytesIO()
        with pd.ExcelWriter(export_buffer, engine='openpyxl') as writer:
            # Physical trades
            if st.session_state.physical_trades:
                pd.DataFrame(st.session_state.physical_trades).to_excel(
                    writer, sheet_name='Physical_Trades', index=False
                )
            # Hedge trades
            if st.session_state.hedge_trades:
                pd.DataFrame(st.session_state.hedge_trades).to_excel(
                    writer, sheet_name='Hedge_Trades', index=False
                )
            # Market prices
            if st.session_state.market_prices:
                pd.DataFrame(st.session_state.market_prices).to_excel(
                    writer, sheet_name='Market_Prices', index=False
                )
            # Metadata
            metadata = pd.DataFrame([{
                'cargo_name': cargo_name,
                'delivery_point': delivery_point,
                'product_category': st.session_state.get('selected_product_category', ''),
                'product_name': st.session_state.get('selected_product_name', ''),
                'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }])
            metadata.to_excel(writer, sheet_name='Metadata', index=False)

        export_buffer.seek(0)
        st.download_button(
            label="Export All Data (Excel)",
            data=export_buffer.getvalue(),
            file_name=f"trading_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No data to export")

    # Import from Excel
    uploaded_data = st.file_uploader(
        "Import Data (Excel)",
        type=['xlsx', 'xls'],
        key='import_data_file',
        help="Upload previously exported Excel file to restore data"
    )

    if uploaded_data is not None:
        if st.button("Confirm Import"):
            try:
                excel_data = pd.ExcelFile(io.BytesIO(uploaded_data.getvalue()))

                # Import physical trades
                if 'Physical_Trades' in excel_data.sheet_names:
                    df_physical = pd.read_excel(excel_data, sheet_name='Physical_Trades')
                    st.session_state.physical_trades = df_physical.to_dict(orient='records')

                # Import hedge trades
                if 'Hedge_Trades' in excel_data.sheet_names:
                    df_hedge = pd.read_excel(excel_data, sheet_name='Hedge_Trades')
                    st.session_state.hedge_trades = df_hedge.to_dict(orient='records')

                # Import market prices
                if 'Market_Prices' in excel_data.sheet_names:
                    df_market = pd.read_excel(excel_data, sheet_name='Market_Prices')
                    st.session_state.market_prices = df_market.to_dict(orient='records')

                st.success("Data imported successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {str(e)}")

product_name = st.session_state.get("selected_product_name", "Custom Product")

# Main interface - Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Trading Operations", "P&L Analysis", "Visualization", "Records View", "Market P&L"])

# Trading operations tab - Combined physical trading and hedging
with tab1:
    # Create sub-tabs for Buy and Sell operations
    sub_tab1, sub_tab2 = st.tabs(["Buy Operations", "Sell Operations"])
    
    # Buy Operations Tab
    with sub_tab1:
       #st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### Buy & Hedge Entry")
        st.markdown("*Simultaneous purchase of physical oil and hedge position entry*")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Add New Buy Operation**")
        with col2:
            if st.button("Add Buy Operation", key="add_buy_op"):
                st.session_state.show_buy_form = True
    
        # Add buy operation form
        if st.session_state.get('show_buy_form', False):
            with st.form("buy_operation_form"):
                st.markdown("**Physical Oil Purchase**")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    today = datetime.now().date()
                    default_buy_date = today
                    if date_range_valid:
                        default_buy_date = min(max(today, purchase_start), purchase_end)
                        buy_date = st.date_input(
                            "Purchase Date",
                            value=default_buy_date,
                            min_value=purchase_start,
                            max_value=purchase_end
                        )
                    else:
                        st.warning("Adjust purchase start and end dates before adding buy operations.")
                        buy_date = st.date_input(
                            "Purchase Date",
                            value=default_buy_date,
                            disabled=True
                        )
                with col2:
                    buy_quantity = st.number_input("Quantity (MT)", value=0.0, step=1000.0, key="buy_qty")
                with col3:
                    buy_price = st.number_input("Buy Price ($/BBL)", value=0.0, step=0.01)
                with col4:
                    buy_premium_discount = st.number_input("Premium/Discount ($/BBL)", value=0.0, step=0.01, key="buy_premium_discount_input", help="Use positive for premium, negative for discount")
                
                st.markdown("**Hedge Position Entry (Optional)**")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    hedge_contract = st.selectbox(
                        "Contract Type",
                        ["None", "GASOIL Mo1", "GASOIL Mo2", "GASOIL Mo3", "Others"],
                        key="buy_hedge_contract"
                    )
                with col2:
                    hedge_volume = st.number_input("Hedge Volume (MT)", value=0.0, step=1000.0, key="buy_hedge_vol",
                                                 help="Use negative for sell hedge")
                with col3:
                    hedge_entry_price = st.number_input("Entry Price ($/BBL)", value=0.0, step=0.01, key="buy_hedge_entry")
                with col4:
                    hedge_date_default = buy_date
                    if date_range_valid:
                        hedge_trade_date = st.date_input(
                            "Hedge Trade Date",
                            value=hedge_date_default,
                            min_value=purchase_start,
                            max_value=purchase_end,
                            key="buy_hedge_trade_date",
                            help="Select the trade date for the hedge position"
                        )
                    else:
                        st.warning("Adjust purchase start and end dates before adding hedge operations.")
                        hedge_trade_date = st.date_input(
                            "Hedge Trade Date",
                            value=hedge_date_default,
                            disabled=True,
                            key="buy_hedge_trade_date"
                        )

                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.form_submit_button("Save Buy Operation"):
                        if not date_range_valid:
                            st.error("Adjust the purchase date range in the sidebar before saving.")
                        elif not (purchase_start <= buy_date <= purchase_end):
                            st.error("Purchase date must fall within the selected start and end dates.")
                        elif buy_quantity != 0:
                            # Add physical trade record (incomplete - no sale price yet)
                            new_trade = {
                                'date': buy_date.strftime('%Y-%m-%d'),
                                'quantity': buy_quantity,
                                'buy_price': buy_price,
                                'buy_premium_discount': buy_premium_discount,
                                'sale_price': 0.0,  # To be filled in sell operation
                                'sale_premium_discount': 0.0,
                                'sale_date': '',
                                'product_name': st.session_state.get('selected_product_name', ''),
                                'product_category': st.session_state.get('selected_product_category', '')
                            }
                            st.session_state.physical_trades.append(new_trade)
                            
                            # Add hedge record if specified
                            if hedge_contract != "None" and hedge_volume != 0:
                                new_hedge = {
                                    'contract': hedge_contract,
                                    'volume': hedge_volume,
                                    'entry_price': hedge_entry_price,
                                    'exit_price': 0.0,  # To be filled in sell operation
                                    'trade_date': hedge_trade_date.strftime('%Y-%m-%d'),
                                    'status': 'Open',
                                    'exit_date': ''
                                }
                                st.session_state.hedge_trades.append(new_hedge)
                            
                            st.session_state.show_buy_form = False
                            st.success("Buy operation added!")
                            st.rerun()
                        else:
                            st.error("Quantity must be greater than zero.")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_buy_form = False
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 🔧 优化：显示pending operations with related hedge information
        incomplete_trades = [trade for trade in st.session_state.physical_trades if trade['sale_price'] == 0.0]
        open_hedges = [hedge for hedge in st.session_state.hedge_trades if hedge['status'] == 'Open']
        
        if incomplete_trades or open_hedges:
            st.markdown("### Current Pending Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Pending Physical Trades**")
                if incomplete_trades:
                    df_incomplete = pd.DataFrame(incomplete_trades)
                    
                    # Add index for reference
                    df_incomplete['ID'] = range(1, len(df_incomplete) + 1)
                    
                    # Format display
                    df_display = df_incomplete.copy()
                    df_display['buy_premium_discount'] = df_display.get('buy_premium_discount', 0.0)
                    df_display['Net Buy Price'] = df_display['buy_price'] + df_display['buy_premium_discount']
                    df_display['Quantity (MT)'] = df_display['quantity'].apply(lambda x: f"{x:,.0f}")
                    df_display['Buy Price ($/BBL)'] = df_display['buy_price'].apply(lambda x: f"${x:.2f}")
                    df_display['Premium/Discount ($/BBL)'] = df_display['buy_premium_discount'].apply(lambda x: f"${x:.2f}")
                    df_display['Net Buy Price ($/BBL)'] = df_display['Net Buy Price'].apply(lambda x: f"${x:.2f}")
                    df_display['Status'] = "Awaiting Sale"
                    if 'product_name' not in df_display.columns:
                        if 'product' in df_display.columns:
                            df_display['product_name'] = df_display['product']
                        else:
                            df_display['product_name'] = ''

                    st.dataframe(
                        df_display[['ID', 'date', 'product_name', 'Quantity (MT)', 'Buy Price ($/BBL)', 'Premium/Discount ($/BBL)', 'Net Buy Price ($/BBL)', 'Status']].rename(columns={'product_name': 'Product'}),
                        width='stretch'
                    )
                else:
                    st.info("No pending physical trades")
            
            with col2:
                st.markdown("**Open Hedge Positions**")
                if open_hedges:
                    df_hedges = pd.DataFrame(open_hedges)
                    
                    # Add index for reference
                    df_hedges['ID'] = range(1, len(df_hedges) + 1)
                    
                    # Format display
                    df_display = df_hedges.copy()
                    df_display['Volume (MT)'] = df_display['volume'].apply(lambda x: f"{x:,.0f}")
                    df_display['Entry Price ($/BBL)'] = df_display['entry_price'].apply(lambda x: f"${x:.2f}")
                    df_display['Type'] = df_display['volume'].apply(lambda x: "Sell Hedge" if x < 0 else "Buy Hedge")
                    df_display['Trade Date'] = df_display['trade_date'] if 'trade_date' in df_display.columns else ''
                    df_display['Expiry'] = df_display['expiry'] if 'expiry' in df_display.columns else ''
                    
                    st.dataframe(
                        df_display[['ID', 'contract', 'Trade Date', 'Volume (MT)', 'Entry Price ($/BBL)', 'Type', 'Expiry']],
                        width='stretch'
                    )
                else:
                    st.info("No open hedge positions")
            
            # Summary section
            if incomplete_trades and open_hedges:
                st.markdown("#### Operations Summary")
                total_physical_volume = sum(trade['quantity'] for trade in incomplete_trades)
                total_hedge_volume = sum(abs(hedge['volume']) for hedge in open_hedges)
                hedge_ratio = (total_hedge_volume / total_physical_volume * 100) if total_physical_volume > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Physical Volume", f"{total_physical_volume:,.0f} MT")
                with col2:
                    st.metric("Total Hedge Volume", f"{total_hedge_volume:,.0f} MT")
                with col3:
                    st.metric("Hedge Ratio", f"{hedge_ratio:.1f}%")

    # Sell Operations Tab
    with sub_tab2:
        #st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### Sell & Hedge Exit")
        st.markdown("*Complete the trading cycle by selling physical oil and closing hedge positions*")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Add New Sell Operation**")
        with col2:
            if st.button("Add Sell Operation", key="add_sell_op"):
                st.session_state.show_sell_form = True
        
        # Add sell operation form
        if st.session_state.get('show_sell_form', False):
            with st.form("sell_operation_form"):
                st.markdown("**Physical Oil Sale**")
                
                # Show available incomplete trades
                incomplete_trades = [(i, trade) for i, trade in enumerate(st.session_state.physical_trades) if trade['sale_price'] == 0.0]
                sale_price = 0.0
                sale_premium_discount = 0.0
                sale_date = datetime.now().date()
                if incomplete_trades:
                    trade_options = [f"Trade {i}: {trade['date']} - {trade['quantity']:,.0f} MT at ${trade['buy_price']:.2f}" 
                                   for i, trade in incomplete_trades]
                    selected_trade_idx = st.selectbox("Select Trade to Complete", range(len(trade_options)), 
                                                     format_func=lambda x: trade_options[x])
                    selected_trade_original_idx = incomplete_trades[selected_trade_idx][0]
                    selected_trade = incomplete_trades[selected_trade_idx][1]
                    
                    buy_premium_value = selected_trade.get('buy_premium_discount', 0.0)
                    default_sale_premium = selected_trade.get('sale_premium_discount', 0.0)
                    net_buy_price = selected_trade['buy_price'] + buy_premium_value

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        sale_date = st.date_input("Sale Date", value=sale_date)
                        st.write(f"Quantity: {selected_trade['quantity']:,.0f} MT")
                        st.write(f"Buy Price: ${selected_trade['buy_price']:.2f}/BBL")
                        st.write(f"Buy Premium/Discount: ${buy_premium_value:.2f}/BBL")
                        st.write(f"Net Buy Price: ${net_buy_price:.2f}/BBL")
                    with col2:
                        sale_price = st.number_input("Sale Price ($/BBL)", value=0.0, step=0.01)
                    with col3:
                        sale_premium_discount = st.number_input(
                            "Sale Premium/Discount ($/BBL)",
                            value=default_sale_premium,
                            step=0.01,
                            key="sale_premium_discount_input",
                            help="Use positive for premium, negative for discount"
                        )
                        net_sale_price = sale_price + sale_premium_discount
                        st.write(f"Net Sale Price: ${net_sale_price:.2f}/BBL")

                    estimated_pnl = (net_sale_price - net_buy_price) * selected_trade['quantity']
                    st.write(f"Estimated P&L: ${estimated_pnl:,.2f}")

                else:
                    st.warning("No pending buy operations to complete. Please add a buy operation first.")
                    selected_trade_original_idx = None
                
                # Hedge exit section
                st.markdown("**Hedge Position Exit (Optional)**")
                open_hedges = [(i, hedge) for i, hedge in enumerate(st.session_state.hedge_trades) if hedge['status'] == 'Open']
                
                # Initialize variables
                selected_hedge_original_idx = None
                selected_hedge = None
                hedge_exit_price = 0.0
                hedge_exit_date = None
                
                if open_hedges:
                    # 🔧 修复：正确解构open_hedges元组
                    hedge_options = []
                    for orig_idx, hedge in open_hedges:
                        trade_date = hedge.get('trade_date', '-')
                        expiry_value = hedge.get('expiry')
                        label = (
                            f"ID {orig_idx+1}: {hedge['contract']} | {hedge['volume']:,.0f} MT | "
                            f"Entry: ${hedge['entry_price']:.2f} | Trade: {trade_date}"
                        )
                        if expiry_value:
                            label += f" | Exp: {expiry_value}"
                        hedge_options.append(label)
                    hedge_options.insert(0, "None - Don't close any hedge")
                    selected_hedge_idx = st.selectbox("Select Hedge to Close", range(len(hedge_options)), 
                                                    format_func=lambda x: hedge_options[x])
                    
                    if selected_hedge_idx > 0:  # Not "None"
                        selected_hedge_original_idx = open_hedges[selected_hedge_idx - 1][0]
                        selected_hedge = open_hedges[selected_hedge_idx - 1][1]
                        
                        # 🔧 优化：使用更突出的界面设计来激活hedge退出功能
                        st.markdown("---")
                        st.markdown("### Hedge Exit Activated")
                        st.markdown("*You have selected a hedge position to close. Please enter exit price below.*")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Selected Hedge Details:**")
                            st.info(f"""
                            **Contract:** {selected_hedge['contract']}  
                            **Volume:** {selected_hedge['volume']:,.0f} MT  
                            **Entry Price:** ${selected_hedge['entry_price']:.2f}/BBL  
                            **Trade Date:** {selected_hedge.get('trade_date', 'N/A')}
                            **Expiry:** {selected_hedge.get('expiry', 'N/A')}
                            """)
                        
                        with col2:
                            st.markdown("**Exit Price Input:**")
                            # 🔧 修复：不使用自动默认值，要求用户主动输入
                            st.write(f"**Reference Entry Price:** ${selected_hedge['entry_price']:.2f}/BBL")
                            hedge_exit_price = st.number_input(
                                "Exit Price ($/BBL)", 
                                value=0.0,  # 修复：使用0.0强制用户输入实际退出价格
                                step=0.01, 
                                key="hedge_exit",
                                help="Enter the actual market price at which you want to exit this hedge position"
                            )

                            default_exit_date = sale_date
                            hedge_exit_date = st.date_input(
                                "Hedge Exit Date",
                                value=default_exit_date,
                                key="hedge_exit_date_input",
                                help="Select the date for closing this hedge position"
                            )

                            # 实时显示P&L计算
                            hedge_pnl = (hedge_exit_price - selected_hedge['entry_price']) * selected_hedge['volume']
                            hedge_type = "Sell Hedge" if selected_hedge['volume'] < 0 else "Buy Hedge"
                            
                            # 🔧 优化：使用颜色编码显示盈亏
                            if hedge_pnl > 0:
                                st.success(f"**Projected Profit:** ${hedge_pnl:,.2f}")
                            elif hedge_pnl < 0:
                                st.error(f"**Projected Loss:** ${hedge_pnl:,.2f}")
                            else:
                                st.info(f"**Break Even:** ${hedge_pnl:,.2f}")
                            
                            st.write(f"**Hedge Type:** {hedge_type}")
                            
                        # 🔧 优化：显示综合操作状态和P&L预览
                        st.markdown("---")
                        st.markdown("### Combined Operation Preview")
                        
                        # 计算individual P&Ls
                        physical_pnl_preview = 0
                        hedge_pnl_preview = 0
                        
                        if incomplete_trades and selected_trade_original_idx is not None and (sale_price > 0 or sale_premium_discount != 0):
                            selected_trade = incomplete_trades[selected_trade_idx][1]
                            buy_premium_preview = selected_trade.get('buy_premium_discount', 0.0)
                            net_sale_preview = sale_price + sale_premium_discount
                            net_buy_preview = selected_trade['buy_price'] + buy_premium_preview
                            physical_pnl_preview = (net_sale_preview - net_buy_preview) * selected_trade['quantity']
                        
                        if hedge_exit_price > 0:
                            hedge_pnl_preview = (hedge_exit_price - selected_hedge['entry_price']) * selected_hedge['volume']
                        
                        combined_pnl = physical_pnl_preview + hedge_pnl_preview
                        
                        # 显示P&L预览
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if physical_pnl_preview != 0:
                                color = "🟢" if physical_pnl_preview > 0 else "🔴"
                                st.metric("Physical P&L", f"${physical_pnl_preview:,.2f}", delta=None)
                            else:
                                st.metric("Physical P&L", "Not calculated", delta=None)
                        
                        with col2:
                            if hedge_pnl_preview != 0:
                                color = "🟢" if hedge_pnl_preview > 0 else "🔴"
                                st.metric("Hedge P&L", f"${hedge_pnl_preview:,.2f}", delta=None)
                            else:
                                st.metric("Hedge P&L", "Not calculated", delta=None)
                        
                        with col3:
                            if physical_pnl_preview != 0 or hedge_pnl_preview != 0:
                                color = "🟢" if combined_pnl > 0 else "🔴"
                                st.metric("Combined P&L", f"${combined_pnl:,.2f}", delta=None)
                            else:
                                st.metric("Combined P&L", "Enter prices", delta=None)
                        
                        # 操作状态提示
                        if hedge_exit_price > 0:
                            if hedge_exit_price != selected_hedge['entry_price']:
                                st.success("Hedge exit price entered! Ready to execute combined operation.")
                            else:
                                st.warning("Exit price equals entry price (break even). Confirm if this is intended.")
                        else:
                            st.info("Enter hedge exit price above to see complete P&L preview.")
                    else:
                        selected_hedge_original_idx = None
                        hedge_exit_price = 0.0
                else:
                    st.info("💡 No open hedge positions to close. Add hedge positions in Buy Operations first.")
                
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.form_submit_button("Complete Sale"):
                        # Check if we have physical trade to complete
                        has_physical_to_complete = (
                            incomplete_trades
                            and selected_trade_original_idx is not None
                            and (sale_price > 0 or sale_premium_discount != 0)
                        )
                        
                        # Check if we have hedge to close
                        has_hedge_to_close = selected_hedge_original_idx is not None and hedge_exit_price > 0
                        
                        # Check if user selected a hedge but didn't enter exit price
                        hedge_selected_but_no_price = (selected_hedge_original_idx is not None and hedge_exit_price <= 0)
                        
                        # Validate operations
                        if hedge_selected_but_no_price:
                            st.error("⚠️ You have selected a hedge position to close but haven't entered an exit price. Please enter the hedge exit price or select 'None' if you don't want to close any hedge position.")
                        elif has_physical_to_complete or has_hedge_to_close:
                            operation_completed = []
                            
                            # Complete physical trade if available
                            if has_physical_to_complete:
                                st.session_state.physical_trades[selected_trade_original_idx]['sale_price'] = sale_price
                                st.session_state.physical_trades[selected_trade_original_idx]['sale_premium_discount'] = sale_premium_discount
                                st.session_state.physical_trades[selected_trade_original_idx]['sale_date'] = sale_date.strftime('%Y-%m-%d')
                                operation_completed.append("Physical sale")
                            
                            # Close hedge if selected
                            if has_hedge_to_close:
                                exit_date_value = hedge_exit_date if hedge_exit_date else sale_date
                                st.session_state.hedge_trades[selected_hedge_original_idx]['exit_price'] = hedge_exit_price
                                st.session_state.hedge_trades[selected_hedge_original_idx]['exit_date'] = exit_date_value.strftime('%Y-%m-%d')
                                st.session_state.hedge_trades[selected_hedge_original_idx]['status'] = 'Closed'
                                operation_completed.append("Hedge position closed")
                            
                            st.session_state.show_sell_form = False
                            success_msg = " and ".join(operation_completed) + " completed!"
                            st.success(success_msg)
                            st.rerun()
                        else:
                            if not incomplete_trades:
                                st.error("No pending physical trades to complete and no hedge positions selected to close.")
                            elif selected_hedge_original_idx is None:
                                st.error("Please select a physical trade to complete or a hedge position to close.")
                            else:
                                st.error("Please complete all required fields (sale price and/or hedge exit price).")
                with col2:
                    if st.form_submit_button("Cancel"):
                        st.session_state.show_sell_form = False
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# P&L analysis tab  
with tab2:
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("### P&L Analysis Results")
    
    # Calculate P&L
    physical_pnl, hedge_pnl, net_pnl = calculate_pnl(
        st.session_state.physical_trades,
        st.session_state.hedge_trades
    )
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    delivery_point_display = delivery_point if delivery_point else "Not specified"

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Cargo / Product</h4>
            <h3>{cargo_name}</h3>
            <p style="margin: 0; color: #6b7280;">{product_name}</p>
            <p style="margin: 0; color: #9ca3af;">Delivery: {delivery_point_display}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_class = "profit-positive" if physical_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>Physical P&L</h4>
            <h3 class="{color_class}">${physical_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color_class = "profit-positive" if hedge_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>Hedge P&L</h4>
            <h3 class="{color_class}">${hedge_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        color_class = "profit-positive" if net_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>Net P&L</h4>
            <h3 class="{color_class}">${net_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed analysis
    if st.session_state.physical_trades or st.session_state.hedge_trades:
        st.markdown("### Detailed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.physical_trades:
                st.markdown("**Physical Trading Details**")
                df_physical = pd.DataFrame(st.session_state.physical_trades)
                df_physical['buy_premium_discount'] = df_physical.get('buy_premium_discount', 0.0)
                df_physical['sale_premium_discount'] = df_physical.get('sale_premium_discount', 0.0)
                total_quantity = df_physical['quantity'].sum()
                avg_buy_price = (df_physical['buy_price'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                avg_sale_price = (df_physical['sale_price'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                avg_buy_premium = (df_physical['buy_premium_discount'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                avg_sale_premium = (df_physical['sale_premium_discount'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                avg_net_buy_price = avg_buy_price + avg_buy_premium
                avg_net_sale_price = avg_sale_price + avg_sale_premium

                st.write(f"- Total Volume: {total_quantity:,.0f} MT")
                st.write(f"- Avg Net Buy Price: ${avg_net_buy_price:.2f}/BBL")
                st.write(f"- Avg Net Sale Price: ${avg_net_sale_price:.2f}/BBL")
                st.write(f"- Unit Profit (Net): ${avg_net_sale_price - avg_net_buy_price:.2f}/BBL")

        
        with col2:
            if st.session_state.hedge_trades:
                st.markdown("**Hedge Trading Details**")
                df_hedge = pd.DataFrame(st.session_state.hedge_trades)
                total_hedge_volume = df_hedge['volume'].sum()
                open_positions = df_hedge[df_hedge['status'] == 'Open']['volume'].sum()
                closed_positions = df_hedge[df_hedge['status'] == 'Closed']['volume'].sum()
                
                st.write(f"- Total Hedge Volume: {total_hedge_volume:,.0f} MT")
                st.write(f"- Open Positions: {open_positions:,.0f} MT")
                st.write(f"- Closed Positions: {closed_positions:,.0f} MT")
                st.write(f"- Hedge Ratio: {abs(total_hedge_volume/total_quantity)*100:.1f}%" if total_quantity != 0 else "- Hedge Ratio: 0%")

# Visualization tab
with tab3:
    st.markdown("### P&L Visualization")
    
    if st.session_state.physical_trades or st.session_state.hedge_trades:
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L distribution pie chart
            labels = ['Physical Trading', 'Hedge Trading']
            values = [abs(physical_pnl), abs(hedge_pnl)]
            colors = ['#3b82f6', '#ef4444']
            
            if sum(values) > 0:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    marker_colors=colors
                )])
                fig_pie.update_layout(
                    title="P&L Composition",
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # P&L comparison bar chart
            categories = ['Physical Trading', 'Hedge Trading', 'Net P&L']
            pnl_values = [physical_pnl, hedge_pnl, net_pnl]
            colors = ['green' if x >= 0 else 'red' for x in pnl_values]
            
            fig_bar = go.Figure(data=[go.Bar(
                x=categories,
                y=pnl_values,
                marker_color=colors,
                text=[f"${x:,.0f}" for x in pnl_values],
                textposition='auto'
            )])
            fig_bar.update_layout(
                title="P&L Comparison Analysis",
                yaxis_title="P&L ($)",
                height=400
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Time series analysis
        if len(st.session_state.physical_trades) > 1:
            st.markdown("### 📅 Trading Time Series")
            df_trades = pd.DataFrame(st.session_state.physical_trades)
            df_trades['date'] = pd.to_datetime(df_trades['date'])
            df_trades['buy_premium_discount'] = df_trades.get('buy_premium_discount', 0.0)
            df_trades['sale_premium_discount'] = df_trades.get('sale_premium_discount', 0.0)
            df_trades['Net Buy Price'] = df_trades['buy_price'] + df_trades['buy_premium_discount']
            df_trades['Net Sale Price'] = df_trades['sale_price'] + df_trades['sale_premium_discount']
            df_trades['Cumulative P&L'] = ((df_trades['Net Sale Price'] - df_trades['Net Buy Price']) * df_trades['quantity']).cumsum()
            
            fig_line = px.line(
                df_trades,
                x='date',
                y='Cumulative P&L',
                title='Cumulative P&L Trend',
                markers=True
            )
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Please add trading data to view visualization charts")

# Records view tab
with tab4:
    st.markdown("### Complete Records View")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Physical Trading Records")
        if st.session_state.physical_trades:
            df_trades = pd.DataFrame(st.session_state.physical_trades)
            if 'product_name' not in df_trades.columns:
                df_trades['product_name'] = ''
            
            # Add calculation columns
            df_trades['buy_premium_discount'] = df_trades.get('buy_premium_discount', 0.0)
            df_trades['sale_premium_discount'] = df_trades.get('sale_premium_discount', 0.0)
            df_trades['Net Buy Price'] = df_trades['buy_price'] + df_trades['buy_premium_discount']
            df_trades['Net Sale Price'] = df_trades['sale_price'] + df_trades['sale_premium_discount']
            df_trades['Unit P&L'] = df_trades.apply(
                lambda row: (row['Net Sale Price'] - row['Net Buy Price']) if row['sale_price'] > 0 else 0.0,
                axis=1
            )
            df_trades['Total P&L'] = df_trades['Unit P&L'] * df_trades['quantity']
            df_trades['Status'] = df_trades['sale_price'].apply(lambda x: 'Completed' if x > 0 else 'Pending')
            
            # Format display
            df_display = df_trades.copy()
            df_display['Quantity (MT)'] = df_display['quantity'].apply(lambda x: f"{x:,.0f}")
            df_display['Buy Price ($/BBL)'] = df_display['buy_price'].apply(lambda x: f"${x:.2f}")
            df_display['Buy Premium/Discount ($/BBL)'] = df_display['buy_premium_discount'].apply(lambda x: f"${x:.2f}")
            df_display['Net Buy Price ($/BBL)'] = df_display['Net Buy Price'].apply(lambda x: f"${x:.2f}")
            df_display['Sale Price ($/BBL)'] = df_display['sale_price'].apply(lambda x: f"${x:.2f}" if x > 0 else 'Pending')
            df_display['Sale Premium/Discount ($/BBL)'] = df_display.apply(lambda row: f"${row['sale_premium_discount']:.2f}" if row['sale_price'] > 0 else '-', axis=1)
            df_display['Net Sale Price ($/BBL)'] = df_display.apply(lambda row: f"${row['Net Sale Price']:.2f}" if row['sale_price'] > 0 else 'Pending', axis=1)
            df_display['Unit P&L ($/BBL)'] = df_display['Unit P&L'].apply(lambda x: f"${x:.2f}" if x != 0 else '-')
            df_display['Total P&L ($)'] = df_display['Total P&L'].apply(lambda x: f"${x:,.2f}" if x != 0 else '-')
            
            st.dataframe(
                df_display[['date', 'product_name', 'Quantity (MT)', 'Buy Price ($/BBL)', 'Buy Premium/Discount ($/BBL)', 'Net Buy Price ($/BBL)', 'Sale Price ($/BBL)', 'Sale Premium/Discount ($/BBL)', 'Net Sale Price ($/BBL)', 'Unit P&L ($/BBL)', 'Total P&L ($)', 'Status']].rename(columns={'product_name': 'Product'}),
                width='stretch'
            )
            
            if st.button("Clear Physical Records", key="clear_physical_records"):
                st.session_state.physical_trades = []
                st.rerun()
        else:
            st.info("No physical trading records yet.")
    
    with col2:
        st.markdown("#### Hedge Trading Records")
        if st.session_state.hedge_trades:
            df_hedges = pd.DataFrame(st.session_state.hedge_trades)
            
            # Add calculation columns
            df_hedges['Unit P&L'] = df_hedges['exit_price'] - df_hedges['entry_price']
            df_hedges['Total P&L'] = df_hedges['Unit P&L'] * df_hedges['volume']
            
            # Format display
            df_display = df_hedges.copy()
            df_display['Volume (MT)'] = df_display['volume'].apply(lambda x: f"{x:,.0f}")
            df_display['Entry Price ($/BBL)'] = df_display['entry_price'].apply(lambda x: f"${x:.2f}")

            if 'trade_date' in df_display.columns:
                df_display['Trade Date'] = df_display['trade_date']
            else:
                df_display['Trade Date'] = ''

            # Improved Exit Price display logic - use status as primary indicator
            def format_exit_price(row):
                if row.get('status', 'Open') == 'Closed' and row['exit_price'] > 0:
                    return f"${row['exit_price']:.2f}"
                elif row.get('status', 'Open') == 'Open':
                    return "Open" if row['exit_price'] == 0 else f"${row['exit_price']:.2f}"
                else:
                    # Handle inconsistent data
                    return f"${row['exit_price']:.2f}" if row['exit_price'] > 0 else "Pending"

            df_display['Exit Price ($/BBL)'] = df_hedges.apply(format_exit_price, axis=1)
            df_display['Unit P&L ($/BBL)'] = df_display['Unit P&L'].apply(lambda x: f"${x:.2f}" if x != 0 else "-")
            df_display['Total P&L ($)'] = df_display['Total P&L'].apply(lambda x: f"${x:,.2f}" if x != 0 else "-")

            st.dataframe(
                df_display[['contract', 'Trade Date', 'Volume (MT)', 'Entry Price ($/BBL)', 'Exit Price ($/BBL)', 'Unit P&L ($/BBL)', 'Total P&L ($)', 'status']],
                width='stretch'
            )
            
            if st.button("Clear Hedge Records", key="clear_hedge_records"):
                st.session_state.hedge_trades = []
                st.rerun()
        else:
            st.info("No hedge trading records yet.")

with tab5:
    st.markdown("### Market Prices & MTM Analysis")
    st.markdown("Upload market prices, pick an as-of date, and review mark-to-market P&L for open physical and hedge positions.")

    if 'sample_market_template_bytes' not in st.session_state:
        sample_template = pd.DataFrame(
            [
                {"date": datetime(2024, 2, 1), "instrument": "180 CST AG MOPAG", "price": 75.40, "type": "Physical"},
                {"date": datetime(2024, 2, 1), "instrument": "GASOIL Mo1", "price": 77.00, "type": "Hedge"},
                {"date": datetime(2024, 2, 2), "instrument": "180 CST AG MOPAG", "price": 74.95, "type": "Physical"},
                {"date": datetime(2024, 2, 2), "instrument": "GASOIL Mo1", "price": 76.25, "type": "Hedge"}
            ]
        )
        sample_buffer = io.BytesIO()
        sample_template.to_excel(sample_buffer, index=False)
        st.session_state.sample_market_template_bytes = sample_buffer.getvalue()

    sample_template_bytes = st.session_state.sample_market_template_bytes

    st.download_button(
        "Download Sample Market Price Template",
        data=sample_template_bytes,
        file_name="market_price_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_market_template"
    )

    with st.expander("Manage Market Prices", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload Market Prices (Excel)",
            type=["xlsx", "xls"],
            help="Template requires columns: date, instrument, price, optional type.",
            key='market_price_file'
        )
        if uploaded_file is not None:
            try:
                uploaded_bytes = uploaded_file.getvalue()
                uploaded_df = pd.read_excel(io.BytesIO(uploaded_bytes))
                normalized_df = normalize_market_price_df(uploaded_df)
                save_market_price_df(normalized_df)
                st.success("Market prices uploaded successfully.")
                st.session_state.market_price_file = None
            except ValueError as err:
                st.error(f"Template issue: {err}")
            except Exception as exc:
                st.error(f"Failed to read file: {exc}")

        editor_df = get_market_price_df().drop(columns=['instrument_key'], errors='ignore')
        if not editor_df.empty and 'instrument' in editor_df.columns:
            editor_df['instrument'] = editor_df['instrument'].astype(str).fillna('')
        if editor_df.empty:
            editor_df = pd.DataFrame({
                'date': pd.Series(dtype='datetime64[ns]'),
                'instrument': pd.Series(dtype='string'),
                'price': pd.Series(dtype='float'),
                'type': pd.Series(dtype='string')
            })

        with st.form("market_price_form"):
            editable_df = st.data_editor(
                editor_df,
                num_rows="dynamic",
                width='stretch',
                column_config={
                    'date': st.column_config.DateColumn("Date"),
                    'instrument': st.column_config.TextColumn("Instrument"),
                    'price': st.column_config.NumberColumn("Market Price ($/BBL)", format="%.2f"),
                    'type': st.column_config.TextColumn("Type")
                },
                hide_index=True
            )
            form_cols = st.columns(2)
            save_prices = form_cols[0].form_submit_button("Save Market Prices")
            clear_prices = form_cols[1].form_submit_button("Clear Market Prices")

        if save_prices:
            manual_df = pd.DataFrame(editable_df)
            if not manual_df.empty and 'instrument' in manual_df.columns:
                manual_df['instrument'] = manual_df['instrument'].astype(str).fillna('')
            save_market_price_df(manual_df)
            st.success("Market prices saved.")

        if clear_prices:
            st.session_state.market_prices = []
            if 'market_price_file' in st.session_state:
                del st.session_state.market_price_file
            st.success("Market prices cleared.")

    market_price_df = get_market_price_df()

    if market_price_df.empty:
        st.info("Add market prices to evaluate mark-to-market P&L.")
    else:
        default_date = st.session_state.get('valuation_date')
        if default_date is None:
            default_date = market_price_df['date'].max().date()
        valuation_date = st.date_input(
            "Valuation Date",
            value=default_date,
            max_value=market_price_df['date'].max().date()
        )
        st.session_state.valuation_date = valuation_date

        pnl_snapshot = evaluate_market_pnl_for_date(
            market_price_df,
            st.session_state.physical_trades,
            st.session_state.hedge_trades,
            valuation_date
        )

        metric_cols = st.columns(3)
        metric_cols[0].metric(
            "Physical MTM",
            f"${pnl_snapshot['physical_pnl']:,.2f}",
            help=f"As of {valuation_date}" 
        )
        metric_cols[1].metric(
            "Hedge MTM",
            f"${pnl_snapshot['hedge_pnl']:,.2f}",
            help=f"As of {valuation_date}" 
        )
        metric_cols[2].metric(
            "Net MTM",
            f"${pnl_snapshot['net_pnl']:,.2f}",
            help=f"As of {valuation_date}" 
        )

        if pnl_snapshot['missing_instruments']:
            st.warning(
                "No market price found for: " + ", ".join(pnl_snapshot['missing_instruments']) +
                f" on {valuation_date}. These exposures are excluded from MTM."
            )

        physical_details = pnl_snapshot['physical_details'].copy()
        hedge_details = pnl_snapshot['hedge_details'].copy()

        if not physical_details.empty:
            physical_details['Market Price ($/BBL)'] = pd.to_numeric(physical_details['Market Price ($/BBL)'], errors='coerce').round(2)
            physical_details['P&L ($)'] = pd.to_numeric(physical_details['P&L ($)'], errors='coerce').round(2)
            st.markdown("#### Physical Position Details")
            st.dataframe(physical_details, width='stretch')

        if not hedge_details.empty:
            hedge_details['Market Price ($/BBL)'] = pd.to_numeric(hedge_details['Market Price ($/BBL)'], errors='coerce').round(2)
            hedge_details['P&L ($)'] = pd.to_numeric(hedge_details['P&L ($)'], errors='coerce').round(2)
            st.markdown("#### Hedge Position Details")
            st.dataframe(hedge_details, width='stretch')

        pnl_series = calculate_market_pnl_series(
            market_price_df,
            st.session_state.physical_trades,
            st.session_state.hedge_trades
        )

        chart_cols = st.columns(2)
        with chart_cols[0]:
            if pnl_series.empty:
                st.info("Add additional price history to see MTM trends.")
            else:
                pnl_fig = go.Figure()
                pnl_fig.add_trace(go.Scatter(
                    x=pnl_series['date'],
                    y=pnl_series['physical_pnl'],
                    mode='lines+markers',
                    name='Physical MTM'
                ))
                pnl_fig.add_trace(go.Scatter(
                    x=pnl_series['date'],
                    y=pnl_series['hedge_pnl'],
                    mode='lines+markers',
                    name='Hedge MTM'
                ))
                pnl_fig.add_trace(go.Scatter(
                    x=pnl_series['date'],
                    y=pnl_series['net_pnl'],
                    mode='lines+markers',
                    name='Net MTM'
                ))
                pnl_fig.update_layout(
                    title='MTM History',
                    xaxis_title='Date',
                    yaxis_title='P&L ($)',
                    hovermode='x unified',
                    legend_title='Category',
                    height=400
                )
                st.plotly_chart(pnl_fig, use_container_width=True)

        with chart_cols[1]:
            relevant_instruments = set(physical_details['Instrument'].dropna().tolist()) | set(hedge_details['Instrument'].dropna().tolist())
            price_history = build_price_history(market_price_df, relevant_instruments)
            if price_history.empty:
                st.info("Upload price history for relevant instruments to view price trends.")
            else:
                price_fig = go.Figure()
                for column in price_history.columns:
                    if column == 'date':
                        continue
                    price_fig.add_trace(go.Scatter(
                        x=price_history['date'],
                        y=price_history[column],
                        mode='lines+markers',
                        name=column
                    ))
                price_fig.update_layout(
                    title='Instrument Price History',
                    xaxis_title='Date',
                    yaxis_title='Price ($/BBL)',
                    hovermode='x unified',
                    height=400
                )
                st.plotly_chart(price_fig, use_container_width=True)

        with st.expander("Raw Market Price Data", expanded=False):
            display_prices = market_price_df.drop(columns=['instrument_key'], errors='ignore').copy()
            display_prices['date'] = display_prices['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(display_prices, width='stretch')

# Footer
footer_logo_html = ""
if logo_base64:
    footer_logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 24px; width: auto; vertical-align: middle; margin-right: 8px;" alt="ABCD Teck">'

st.markdown(f"""
<div class="footer">
    <div style="margin-bottom: 0.5rem;">
        {footer_logo_html}
        <span style="font-weight: 600; color: #374151;">Oil Trading P&L Analysis System</span>
    </div>
    <div>
        <a href="https://www.abcdteck.com" target="_blank">ABCD Teck</a>
        <span style="margin: 0 0.5rem; color: #d1d5db;">|</span>
        <span>CL Risk Consulting</span>
        <span style="margin: 0 0.5rem; color: #d1d5db;">|</span>
        <span style="color: #9ca3af;">Professional Risk Management Solutions</span>
    </div>
</div>
""", unsafe_allow_html=True)