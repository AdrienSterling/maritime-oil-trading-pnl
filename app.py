import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Maritime Oil Trading P&L Analysis System",
    page_icon="🚢",
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
    <h1>🚢 Maritime Oil Trading P&L Analysis System</h1>
</div>
""", unsafe_allow_html=True)

# Calculation functions
def calculate_pnl(physical_trades, hedge_trades):
    """Calculate P&L"""
    # Physical trading P&L
    physical_pnl = 0
    for trade in physical_trades:
        if trade['quantity'] != 0:
            pnl = (trade['sale_price'] - trade['buy_price']) * trade['quantity']
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
    st.markdown("### 📋 Basic Information")
    
    cargo_name = st.text_input(
        "Cargo Name", 
        value="GO-KAKI STAR 0.5%",
        help="Enter vessel name"
    )
    
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
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Reset All Data"):
        st.session_state.physical_trades = []
        st.session_state.hedge_trades = []
        st.rerun()
    
    if st.button("📊 Load Sample Data"):
        st.session_state.physical_trades = [{
            'date': '2019-01-15',
            'quantity': 245778,
            'buy_price': 72.46,
            'sale_price': 78.96
        }]
        st.session_state.hedge_trades = [{
            'contract': 'GASOIL 500PPM Mo1',
            'volume': -245778,
            'entry_price': 75.87,
            'exit_price': 81.98,
            'expiry': '2019-03-01'
        }]
        st.rerun()

# Main interface - Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📦 Physical Trading", "🛡️ Futures Hedging", "📊 P&L Analysis", "📈 Visualization"])

# Physical trading tab
with tab1:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 📦 Physical Trading Records")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Add New Trading Record**")
    with col2:
        if st.button("➕ Add Record", key="add_physical"):
            st.session_state.show_physical_form = True
    
    # Add trading record form
    if st.session_state.get('show_physical_form', False):
        with st.form("physical_trade_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trade_date = st.date_input("Trade Date", value=datetime.now().date())
            with col2:
                quantity = st.number_input("Quantity (MT)", value=0.0, step=1000.0)
            with col3:
                buy_price = st.number_input("Buy Price ($/BBL)", value=0.0, step=0.01)
            with col4:
                sale_price = st.number_input("Sale Price ($/BBL)", value=0.0, step=0.01)
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.form_submit_button("💾 Save"):
                    if quantity != 0:
                        new_trade = {
                            'date': trade_date.strftime('%Y-%m-%d'),
                            'quantity': quantity,
                            'buy_price': buy_price,
                            'sale_price': sale_price
                        }
                        st.session_state.physical_trades.append(new_trade)
                        st.session_state.show_physical_form = False
                        st.success("Trading record added!")
                        st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_physical_form = False
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display existing trading records
    if st.session_state.physical_trades:
        st.markdown("### 📋 Current Trading Records")
        df_trades = pd.DataFrame(st.session_state.physical_trades)
        
        # Add calculation columns
        df_trades['Unit P&L'] = df_trades['sale_price'] - df_trades['buy_price']
        df_trades['Total P&L'] = df_trades['Unit P&L'] * df_trades['quantity']
        
        # Format display
        df_display = df_trades.copy()
        df_display['Quantity (MT)'] = df_display['quantity'].apply(lambda x: f"{x:,.0f}")
        df_display['Buy Price ($/BBL)'] = df_display['buy_price'].apply(lambda x: f"${x:.2f}")
        df_display['Sale Price ($/BBL)'] = df_display['sale_price'].apply(lambda x: f"${x:.2f}")
        df_display['Unit P&L ($/BBL)'] = df_display['Unit P&L'].apply(lambda x: f"${x:.2f}")
        df_display['Total P&L ($)'] = df_display['Total P&L'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            df_display[['date', 'Quantity (MT)', 'Buy Price ($/BBL)', 'Sale Price ($/BBL)', 'Unit P&L ($/BBL)', 'Total P&L ($)']],
            use_container_width=True
        )
        
        if st.button("🗑️ Clear All Records", key="clear_physical"):
            st.session_state.physical_trades = []
            st.rerun()

# Futures hedging tab
with tab2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("### 🛡️ Futures Hedging Records")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Add New Hedge Record**")
    with col2:
        if st.button("➕ Add Hedge", key="add_hedge"):
            st.session_state.show_hedge_form = True
    
    # Add hedge record form
    if st.session_state.get('show_hedge_form', False):
        with st.form("hedge_trade_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                contract = st.selectbox(
                    "Contract Type",
                    ["GASOIL 500PPM Mo1", "GASOIL 500PPM Mo2", "GASOIL 500PPM Mo3", "Others"]
                )
                volume = st.number_input("Hedge Volume (MT)", value=0.0, step=1000.0, 
                                       help="Negative for sell hedge, positive for buy hedge")
                entry_price = st.number_input("Entry Price ($/BBL)", value=0.0, step=0.01)
            
            with col2:
                expiry_date = st.date_input("Expiry Date", value=datetime.now().date())
                exit_price = st.number_input("Exit Price ($/BBL)", value=0.0, step=0.01)
                status = st.selectbox("Status", ["Open", "Closed"])
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.form_submit_button("💾 Save"):
                    if volume != 0:
                        new_hedge = {
                            'contract': contract,
                            'volume': volume,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'expiry': expiry_date.strftime('%Y-%m-%d'),
                            'status': status
                        }
                        st.session_state.hedge_trades.append(new_hedge)
                        st.session_state.show_hedge_form = False
                        st.success("Hedge record added!")
                        st.rerun()
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_hedge_form = False
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display existing hedge records
    if st.session_state.hedge_trades:
        st.markdown("### 📋 Current Hedge Records")
        df_hedges = pd.DataFrame(st.session_state.hedge_trades)
        
        # Add calculation columns
        df_hedges['Unit P&L'] = df_hedges['exit_price'] - df_hedges['entry_price']
        df_hedges['Total P&L'] = df_hedges['Unit P&L'] * df_hedges['volume']
        
        # Format display
        df_display = df_hedges.copy()
        df_display['Volume (MT)'] = df_display['volume'].apply(lambda x: f"{x:,.0f}")
        df_display['Entry Price ($/BBL)'] = df_display['entry_price'].apply(lambda x: f"${x:.2f}")
        df_display['Exit Price ($/BBL)'] = df_display['exit_price'].apply(lambda x: f"${x:.2f}")
        df_display['Unit P&L ($/BBL)'] = df_display['Unit P&L'].apply(lambda x: f"${x:.2f}")
        df_display['Total P&L ($)'] = df_display['Total P&L'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            df_display[['contract', 'Volume (MT)', 'Entry Price ($/BBL)', 'Exit Price ($/BBL)', 'Unit P&L ($/BBL)', 'Total P&L ($)', 'expiry', 'status']],
            use_container_width=True
        )
        
        if st.button("🗑️ Clear All Records", key="clear_hedge"):
            st.session_state.hedge_trades = []
            st.rerun()

# P&L analysis tab
with tab3:
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("### 📊 P&L Analysis Results")
    
    # Calculate P&L
    physical_pnl, hedge_pnl, net_pnl = calculate_pnl(
        st.session_state.physical_trades,
        st.session_state.hedge_trades
    )
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🚢 Cargo Name</h4>
            <h3>{cargo_name}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_class = "profit-positive" if physical_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>📦 Physical P&L</h4>
            <h3 class="{color_class}">${physical_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color_class = "profit-positive" if hedge_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>🛡️ Hedge P&L</h4>
            <h3 class="{color_class}">${hedge_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        color_class = "profit-positive" if net_pnl >= 0 else "profit-negative"
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 Net P&L</h4>
            <h3 class="{color_class}">${net_pnl:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed analysis
    if st.session_state.physical_trades or st.session_state.hedge_trades:
        st.markdown("### 📋 Detailed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.physical_trades:
                st.markdown("**Physical Trading Details**")
                df_physical = pd.DataFrame(st.session_state.physical_trades)
                total_quantity = df_physical['quantity'].sum()
                avg_buy_price = (df_physical['buy_price'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                avg_sale_price = (df_physical['sale_price'] * df_physical['quantity']).sum() / total_quantity if total_quantity != 0 else 0
                
                st.write(f"- Total Volume: {total_quantity:,.0f} MT")
                st.write(f"- Avg Buy Price: ${avg_buy_price:.2f}/BBL")
                st.write(f"- Avg Sale Price: ${avg_sale_price:.2f}/BBL")
                st.write(f"- Unit Profit: ${avg_sale_price - avg_buy_price:.2f}/BBL")
        
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
with tab4:
    st.markdown("### 📈 P&L Visualization")
    
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
            df_trades['Cumulative P&L'] = ((df_trades['sale_price'] - df_trades['buy_price']) * df_trades['quantity']).cumsum()
            
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
        st.info("📝 Please add trading data to view visualization charts")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6b7280;'>"
    "🚢 Maritime Oil Trading P&L Analysis System | Professional POC"
    "</div>",
    unsafe_allow_html=True
)