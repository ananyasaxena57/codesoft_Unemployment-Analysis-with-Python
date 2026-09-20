import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

csv_file = "Unemployment in India.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"'{csv_file}' not found. Please verify the file path.")

# 1. Ingestion & Column Normalization
df = pd.read_csv(csv_file)
df.columns = df.columns.str.strip()
df.dropna(subset=['Region', 'Date', 'Estimated Unemployment Rate (%)'], inplace=True)

# 2. Date parsing and Period tagging
df['Date'] = pd.to_datetime(df['Date'].astype(str).str.strip(), dayfirst=True)
lockdown_date = pd.Timestamp('2020-03-24')
df['Period'] = df['Date'].apply(lambda d: 'Lockdown (Post-Mar 2020)' if d >= lockdown_date else 'Pre-Lockdown')

# 3. Metric: Net Unemployment Shock (Post vs Pre Lockdown Delta per State)
pivot_rates = df.pivot_table(
    index='Region', 
    columns='Period', 
    values='Estimated Unemployment Rate (%)', 
    aggfunc='mean'
).dropna()

pivot_rates['Unemployment Shock (% pts)'] = (
    pivot_rates['Lockdown (Post-Mar 2020)'] - pivot_rates['Pre-Lockdown']
)
top_shocked = pivot_rates.sort_values(by='Unemployment Shock (% pts)', ascending=True).tail(10)

# Visualization 1: Interactive Shock Bar Chart
fig_shock = px.bar(
    top_shocked,
    x='Unemployment Shock (% pts)',
    y=top_shocked.index,
    orientation='h',
    color='Unemployment Shock (% pts)',
    color_continuous_scale='Reds',
    title='Top 10 States by Absolute Unemployment Surge (Post vs Pre-Lockdown)',
    labels={'x': 'Increase in Unemployment Rate (% points)', 'Region': 'State'}
)
fig_shock.update_layout(template='plotly_white', coloraxis_showscale=False)
fig_shock.write_html('unemployment_shock_states.html')

# 4. Metric: Labour Participation vs Unemployment Rate (Rural vs Urban)
fig_scatter = px.scatter(
    df,
    x='Estimated Labour Participation Rate (%)',
    y='Estimated Unemployment Rate (%)',
    color='Area',
    size='Estimated Employed',
    hover_name='Region',
    facet_col='Period',
    opacity=0.7,
    title='Labour Participation vs. Unemployment Rate by Sector and Phase',
    template='plotly_white'
)
fig_scatter.write_html('participation_vs_unemployment.html')

print("Analysis complete. Generated interactive reports:")
print("- unemployment_shock_states.html")
print("- participation_vs_unemployment.html")
