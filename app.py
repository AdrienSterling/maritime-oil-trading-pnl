import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px


PRODUCT_CATALOG = {
    "Crude Oil": [
        "Dubai",
        "Oman",
        "Murban (Abu Dhabi)",
        "Basrah Light (Iraq)",
        "Basrah Heavy (Iraq)",
        "Arab Light (Saudi Arabia)",
        "Arab Heavy (Saudi Arabia)",
        "Kirkuk (Iraq)",
        "ESPO"
    ],
    "Refined Products": [
        "Gasoline",
        "Diesel / Gasoil (10 ppm)",
        "Diesel / Gasoil (500 ppm)",
        "Jet Fuel / Aviation Kerosene",
        "Naphtha",
        "Fuel Oil (HSFO)",
        "Fuel Oil (VLSFO)",
        "Marine Gas Oil (MGO)",
        "Bitumen / Asphalt"
    ],
    "Gas / LNG / LPG": [
        "LNG",
        "LPG - Propane",
        "LPG - Butane",
        "Condensate"
    ],
    "Optional / Custom": [
        "Petchem Feedstocks",
        "Other Crude / Custom Product"
    ]
}


# Page configuration

# Page configuration
st.set_page_config(
    page_title="Maritime Oil Trading P&L Analysis System",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2rem;
    }
    
    .input-section {
        background-color: #fffbeb;
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .result-section {
        background-color: #eff6ff;
        border: 2px solid #3b82f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .profit-positive {
        color: #059669;
        font-weight: bold;
    }
    
    .profit-negative {
        color: #dc2626;
        font-weight: bold;
    }
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>Maritime Oil Trading P&L Analysis System</h1>
</div>
""", unsafe_allow_html=True)

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

# Initialize session state
if 'physical_trades' not in st.session_state:
    st.session_state.physical_trades = []
if 'hedge_trades' not in st.session_state:
    st.session_state.hedge_trades = []

# Sidebar - Basic Information
with st.sidebar:
    st.markdown("### Basic Information")
    
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


    product_category = st.selectbox(
        "Product Category",
        list(PRODUCT_CATALOG.keys()),
        help="Select the broader commodity family"
    )

    product_options = PRODUCT_CATALOG[product_category]

    product_selection = st.selectbox(
        "Product",
        product_options,
        help="Choose the specific product within the selected category"
    )

    custom_product_name = ""
    if product_selection == "Other Crude / Custom Product":
        custom_product_name = st.text_input(
            "Custom Product Name",
            value=st.session_state.get("custom_product_name", ""),
            help="Enter a custom product name if it is not listed"
        )
        if custom_product_name:
            st.session_state.custom_product_name = custom_product_name
    else:
        st.session_state.pop("custom_product_name", None)

    product_name = custom_product_name.strip() if custom_product_name else product_selection
    if not product_name:
        product_name = "Custom Product"

    st.session_state.selected_product_name = product_name

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
        st.rerun()
    
    if st.button("Load Sample Data"):
        st.session_state.physical_trades = [{
            'date': '2019-01-15',
            'quantity': 245778,
            'buy_price': 72.46,
            'buy_premium_discount': 0.0,
            'sale_price': 78.96,
            'sale_premium_discount': 0.0
        }]
        st.session_state.hedge_trades = [{
            'contract': 'GASOIL Mo1',
            'volume': -245778,
            'entry_price': 75.87,
            'exit_price': 81.98,
            'trade_date': '2019-01-15',
            'status': 'Closed'
        }]
        st.rerun()

product_name = st.session_state.get("selected_product_name", "Custom Product")

# Main interface - Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Trading Operations", "P&L Analysis", "Visualization", "Records View"])

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
                                'sale_premium_discount': 0.0
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
                                    'status': 'Open'
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
                    
                    st.dataframe(
                        df_display[['ID', 'date', 'Quantity (MT)', 'Buy Price ($/BBL)', 'Premium/Discount ($/BBL)', 'Net Buy Price ($/BBL)', 'Status']],
                        use_container_width=True
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
                        use_container_width=True
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
                        sale_date = st.date_input("Sale Date", value=datetime.now().date())
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
                                operation_completed.append("Physical sale")
                            
                            # Close hedge if selected
                            if has_hedge_to_close:
                                st.session_state.hedge_trades[selected_hedge_original_idx]['exit_price'] = hedge_exit_price
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
                df_display[['date', 'Quantity (MT)', 'Buy Price ($/BBL)', 'Buy Premium/Discount ($/BBL)', 'Net Buy Price ($/BBL)', 'Sale Price ($/BBL)', 'Sale Premium/Discount ($/BBL)', 'Net Sale Price ($/BBL)', 'Unit P&L ($/BBL)', 'Total P&L ($)', 'Status']],
                use_container_width=True
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
                use_container_width=True
            )
            
            if st.button("Clear Hedge Records", key="clear_hedge_records"):
                st.session_state.hedge_trades = []
                st.rerun()
        else:
            st.info("No hedge trading records yet.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280;'>"
    "Maritime Oil Trading P&L Analysis System | "
    "<a href='https://www.abcdteck.com' target='_blank' style='color: #3b82f6; text-decoration: none;'>ABCD Teck</a> | "
    "CL Risk Consulting"
    "</div>",
    unsafe_allow_html=True
)