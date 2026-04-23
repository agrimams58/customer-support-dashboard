# Customer Support Operations Dashboard

End-to-end MIS reporting project: raw ticket data → Python cleaning → Power BI dashboard → executive summary.

## Business Questions

1. What is the overall SLA compliance rate, and how does it vary by priority,
   channel, and ticket type?
2. Which ticket segments (priority × channel) show the highest breach
   concentration, and what's the monthly trend?
3. How does resolution time correlate with customer satisfaction — is faster
   always better?
4. What does the aging profile of unresolved tickets look like, and which
   channels have the oldest unresolved queues?

## Stack

- Python (pandas) for cleaning + feature engineering
- Power BI for modeling + visualization
- DAX for measures

## How to Reproduce

1. Drop raw CSV into `data/raw/`
2. Run `python src/clean_data.py`
3. Open `powerbi/dashboard.pbix`

## Data Notes

### Data Source

Kaggle: Suraj520's Customer Support Tickets Dataset (8,469 tickets, 17 columns).

### SLA Definition

The dataset lacks a ticket-creation timestamp. SLA is defined as **agent handle
time**: the duration between `First Response Time` and `Time to Resolution`.
SLA thresholds by priority:

- Critical: 4 hours
- High: 24 hours
- Medium: 48 hours
- Low: 72 hours

### Status Distribution (N=8,469)

- Closed: 2,769 (32.7%) — full resolution + CSAT data available
- Open: 2,819 (33.3%)
- Pending Customer Response: 2,881 (34.0%)

### Metric Denominators

- SLA Compliance %, Avg Resolution Hours, Avg CSAT → computed over Closed
  tickets only (N=2,769)
- Volume, channel-mix, time-series → computed over all tickets (N=8,469)
- Open tickets feed aging-bucket analysis (no resolution timestamp)

### Known Data Quirks

- `Date of Purchase` is product purchase date, not ticket creation — not used for SLA
- `Resolution` column contains free-text agent notes (not dates), despite its name
- All timestamps cluster around 2023-06-01 — typical of generated Kaggle data;
  doesn't affect the modeling approach
- **All tickets resolve within 24 hours** due to the generator clustering
  timestamps on 2023-06-01. As a result, only Critical-priority tickets
  experience SLA breaches in the analysis. Industry-standard SLA thresholds
  are preserved (4h / 24h / 48h / 72h) because methodology — not synthetic
  breach counts — is what the dashboard demonstrates.
- **Priority-blind resolution:** Average resolution time is flat across
  priorities (~7.5h for all four), suggesting the Kaggle generator assigned
  priority independently of actual handling speed. In production this
  pattern would indicate agents not respecting priority queues — a flag
  for workflow review.
