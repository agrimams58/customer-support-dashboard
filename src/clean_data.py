"""
Customer Support Operations Dashboard — Data Cleaning Pipeline

Reads raw ticket data, applies MIS-standard cleaning + feature engineering,
and writes two CSVs: tickets_clean.csv and date_dim.csv.

Run from the project root:
    python src/clean_data.py
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from pathlib import Path

# --- Paths ---
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / 'data' / 'raw' / 'customer_support_tickets.csv'
PROCESSED_DIR = ROOT / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# --- Load ---
print(f"Loading {RAW_PATH}...")
df = pd.read_csv(RAW_PATH)
print(f"  {len(df):,} rows × {df.shape[1]} columns")

# --- 1. Standardize column names ---
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

# --- 2. Parse dates ---
for col in ['date_of_purchase', 'first_response_time', 'time_to_resolution']:
    df[col] = pd.to_datetime(df[col], errors='coerce')

# --- 3. Standardize categoricals ---
for col in ['ticket_type', 'ticket_priority', 'ticket_channel',
            'ticket_status', 'customer_gender']:
    df[col] = df[col].astype(str).str.strip().str.title()

# --- 4. Resolution time + data quality flag ---
raw_resolution = (
    (df['time_to_resolution'] - df['first_response_time'])
    .dt.total_seconds() / 3600
)
df['dq_negative_duration'] = raw_resolution < 0
df['resolution_time_hours'] = raw_resolution.abs().round(2)

# --- 5. SLA targets + breach flag ---
SLA_TARGETS = {'Critical': 4, 'High': 24, 'Medium': 48, 'Low': 72}
df['sla_target_hours'] = df['ticket_priority'].map(SLA_TARGETS)
df['sla_breached'] = np.where(
    df['resolution_time_hours'].notna() &
    (df['resolution_time_hours'] > df['sla_target_hours']),
    True, False
)

# --- 6. Aging bucket ---
def age_bucket(hours):
    if pd.isna(hours): return 'Unresolved'
    if hours <= 24: return '0-24h'
    if hours <= 48: return '24-48h'
    if hours <= 72: return '48-72h'
    return '72h+'
df['aging_bucket'] = df['resolution_time_hours'].apply(age_bucket)

# --- 7. Time dimensions ---
df['response_year']        = df['first_response_time'].dt.year
df['response_month']       = df['first_response_time'].dt.to_period('M').astype(str)
df['response_month_name']  = df['first_response_time'].dt.strftime('%b %Y')
df['response_week']        = df['first_response_time'].dt.isocalendar().week
df['response_day_of_week'] = df['first_response_time'].dt.day_name()
df['response_date']        = df['first_response_time'].dt.date
df['response_hour']        = df['first_response_time'].dt.hour

# --- 8. Export cleaned ticket data ---
cols_to_export = [
    'ticket_id', 'customer_age', 'customer_gender',
    'product_purchased', 'date_of_purchase',
    'ticket_type', 'ticket_subject',
    'ticket_status', 'ticket_priority', 'ticket_channel',
    'first_response_time', 'time_to_resolution',
    'resolution_time_hours', 'sla_target_hours', 'sla_breached',
    'aging_bucket', 'dq_negative_duration',
    'customer_satisfaction_rating',
    'response_year', 'response_month', 'response_month_name',
    'response_week', 'response_day_of_week', 'response_date', 'response_hour'
]
df_clean = df[cols_to_export].copy()
df_clean.to_csv(PROCESSED_DIR / 'tickets_clean.csv', index=False)
print(f"Wrote {PROCESSED_DIR / 'tickets_clean.csv'} "
      f"({len(df_clean):,} rows × {df_clean.shape[1]} cols)")

# --- 9. Build date dimension ---
min_date = df['first_response_time'].min().normalize()
max_date = df['first_response_time'].max().normalize()

date_range = pd.date_range(min_date - timedelta(days=2),
                           max_date + timedelta(days=2), freq='D')

date_dim = pd.DataFrame({'date': date_range})
date_dim['year']        = date_dim['date'].dt.year
date_dim['quarter']     = date_dim['date'].dt.quarter
date_dim['month']       = date_dim['date'].dt.month
date_dim['month_name']  = date_dim['date'].dt.strftime('%b %Y')
date_dim['week']        = date_dim['date'].dt.isocalendar().week
date_dim['day']         = date_dim['date'].dt.day
date_dim['day_of_week'] = date_dim['date'].dt.day_name()
date_dim['is_weekend']  = date_dim['date'].dt.dayofweek.isin([5, 6])
date_dim.to_csv(PROCESSED_DIR / 'date_dim.csv', index=False)
print(f"Wrote {PROCESSED_DIR / 'date_dim.csv'} ({len(date_dim)} rows)")

# --- 10. Summary ---
print("\n=== Cleaning complete ===")
print(f"Total tickets:     {len(df):,}")
print(f"Closed tickets:    {(df['ticket_status'] == 'Closed').sum():,}")
print(f"SLA breaches:      {df['sla_breached'].sum():,}")
print(f"Overall SLA %:     "
      f"{(1 - df[df['ticket_status']=='Closed']['sla_breached'].mean())*100:.1f}%")