#!/usr/bin/env python3

# Analysis of Excel hedge calculation logic
hedge_volume = -245778  # Negative number indicates sell hedge
entry_price = 75.87     # Entry price
exit_price = 81.98      # Exit price

print('Excel Hedge Calculation Analysis:')
print(f'Hedge Volume: {hedge_volume:,.0f} MT (sell hedge)')
print(f'Entry Price: ${entry_price:.2f}/BBL')
print(f'Exit Price: ${exit_price:.2f}/BBL')
print(f'Price Movement: ${exit_price - entry_price:.2f}/BBL (price increased)')
print()

# For sell hedge (negative volume):
# When price increases, hedge should be a loss
pnl_formula1 = (entry_price - exit_price) * hedge_volume
pnl_formula2 = (exit_price - entry_price) * hedge_volume

print(f'Formula 1: (Entry - Exit) * Volume = ${pnl_formula1:,.2f}')
print(f'Formula 2: (Exit - Entry) * Volume = ${pnl_formula2:,.2f}')
print()

# Excel shows hedge P&L as -1,481,736.92
expected_hedge_pnl = -1481736.92
print(f'Expected Excel Result: ${expected_hedge_pnl:,.2f}')

# The correct formula should be: (Exit Price - Entry Price) * Volume
correct_pnl = (exit_price - entry_price) * hedge_volume
print(f'Correct Formula: (Exit - Entry) * Volume = ${correct_pnl:,.2f}')

print()
print('Physical P&L verification:')
phys_quantity = 245778
buy_price = 72.46  
sale_price = 78.96
phys_pnl = (sale_price - buy_price) * phys_quantity
print(f'Physical P&L: ${phys_pnl:,.2f}')

net_pnl = phys_pnl + correct_pnl
print(f'Net P&L: ${net_pnl:,.2f}')

# Check if this matches Excel
expected_net = 116311.64
print(f'Expected Net P&L: ${expected_net:,.2f}')
print(f'Difference: ${abs(net_pnl - expected_net):.2f}')