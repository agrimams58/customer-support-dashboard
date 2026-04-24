# Customer Support Operations Dashboard

A portfolio project exploring how a customer support operation can track SLA compliance, ticket aging, and channel-level performance. Built end-to-end from a raw Kaggle dataset of 8,469 tickets through a Python cleaning pipeline, a three-page Power BI dashboard, and a one-page executive PDF.

I took this on to practice what a real MIS / operations analyst workflow might look like — from first opening a messy CSV to handing someone a deliverable they could actually use.

---

## 📊 Dashboard Preview

### Executive Summary

![Executive Summary](outputs/screenshots/01_executive_summary.png)

### SLA & Aging Analysis

![SLA Analysis](outputs/screenshots/02_sla_aging_analysis.png)

### Channel & Type Performance

![Channel Performance](outputs/screenshots/03_channel_type_performance.png)

📄 **[Download Executive Summary PDF](https://github.com/agrimams58/customer-support-dashboard/raw/main/outputs/executive_summary.pdf)**

---

## 🎯 What the Data Showed

| Metric                        | Value                       | Observation                                                      |
| ----------------------------- | --------------------------- | ---------------------------------------------------------------- |
| Overall SLA Compliance        | **82.6%**                   | Slightly below the 85% benchmark that most support teams aim for |
| Critical-Priority Breach Rate | **66.3%**                   | All 481 SLA breaches come from Critical tickets                  |
| Best Channel (CSAT × Speed)   | **Chat**                    | 7.5h average resolution, 3.15 CSAT                               |
| Weakest Segment               | **Email · Product Inquiry** | 75.4% SLA compliance — the lowest in the dataset                 |

The data points to one pattern worth noting: **resolution times are nearly identical across all four priority levels** (~7.5h each). Normally Critical tickets should resolve faster than Low-priority ones, so this uniform distribution is interesting — it may suggest that priority labels aren't translating into queue ordering. As a result, Critical tickets (with a strict 4-hour SLA) end up breaching at 66%, while Low-priority tickets (allowed 72 hours) never breach.

I found this kind of finding motivating — not because it proves anything conclusively, but because it's the sort of thing an analyst might flag to the operations team and investigate further.

---

## 🛠️ Stack

- **Python 3.14** with pandas, numpy, reportlab
- **Jupyter Lab** for exploration
- **Power BI Desktop** for the dashboard (star schema, DAX measures)
- **Git / GitHub** for version control

---

## 📁 Project Structure

```
customer-support-dashboard/
├── data/
│ ├── raw/ # Kaggle CSV goes here (gitignored)
│ └── processed/ # Cleaned data (gitignored)
├── notebooks/
│ ├── 01_exploration.ipynb # Getting to know the dataset
│ └── 02_cleaning.ipynb # Building the cleaning logic
├── src/
│ ├── clean_data.py # Production-style cleaning script
│ └── build_pdf.py # PDF report generator
├── powerbi/
│ └── dashboard.pbix # Power BI file
├── outputs/
│ ├── screenshots/ # Dashboard page PNGs
│ └── executive_summary.pdf # One-page deliverable
├── requirements.txt
└── README.md
```

---

## 🔬 How I Approached It

### Data Source

[Kaggle: Customer Support Tickets Dataset by Suraj520](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) — 8,469 tickets, 17 columns.

### Defining SLA for This Data

The dataset doesn't include a true ticket-creation timestamp, so I calculated SLA as **agent handle time** — the duration between `First Response Time` and `Time to Resolution`. I used industry-standard priority thresholds:

| Priority | SLA Target | Tickets | Breach Rate |
| -------- | ---------- | ------- | ----------- |
| Critical | 4 hours    | 2,129   | 66.3%       |
| High     | 24 hours   | 2,085   | 0%          |
| Medium   | 48 hours   | 2,192   | 0%          |
| Low      | 72 hours   | 2,063   | 0%          |

### Why I Kept the Nulls

This was an early design decision I thought about carefully. Nulls in columns like `resolution_time_hours`, `sla_breached`, and `customer_satisfaction_rating` aren't data quality issues — they mean the event hasn't happened yet (Open and Pending tickets don't have a resolution time).

Filling those with zeros or means would have corrupted the KPIs (e.g., Avg Resolution Time would drop because I'd be averaging in fake zeros). Instead, I left the nulls as-is — pandas and DAX both skip nulls in aggregations automatically, so metrics compute correctly over the appropriate population (2,769 Closed tickets for SLA metrics, 8,469 for volume).

### A Data Quality Issue I Found and Fixed

During exploration, I noticed that 1,365 of 2,769 Closed tickets (49%) had `time_to_resolution` earlier than `first_response_time` — which is physically impossible. The Kaggle generator seems to have assigned both timestamps as random times within the same day without enforcing order.

I decided to take the absolute value of the duration and added a `dq_negative_duration` flag column so the fix is auditable. This felt like the most honest approach — fix the data, but make the fix visible.

### One Thing the Synthetic Data Can't Show

All timestamps cluster within a 48-hour window around June 1, 2023, so no resolution time exceeds 24 hours. This means only Critical tickets (with a 4-hour SLA) ever breach in this dataset; High/Medium/Low are all at 100% compliance by default.

I kept the industry-standard thresholds anyway because the point of the project is the methodology — when this pipeline runs on real data with longer resolutions, the full aging and breach logic will populate naturally.

### Star Schema Model

The Power BI model uses a fact table (`tickets_clean`) joined to a dedicated date dimension (`date_dim`). I did this because it's the convention for production BI work — it enables proper time intelligence in DAX and keeps the model extensible if more fact tables get added later.

---

## ▶️ Running This Project Yourself

### Prerequisites

- Python 3.10+
- Power BI Desktop (Windows-only)
- A Kaggle account

### Steps

```bash
# Clone the repo
git clone https://github.com/agrimams58/customer-support-dashboard.git
cd customer-support-dashboard

# Create a virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Download the dataset from Kaggle (link above)
# Save customer_support_tickets.csv into data/raw/

# Run the cleaning pipeline
python src/clean_data.py

# Generate the executive PDF
python src/build_pdf.py

# Open the dashboard
# Open powerbi/dashboard.pbix in Power BI Desktop
```

---

## 💡 Skills I Practiced

- **End-to-end data flow** — moving data from raw CSV through cleaning, modeling, visualization, and a final deliverable
- **Python with pandas** — feature engineering, null handling, date parsing, applying business rules
- **Data quality thinking** — spotting the negative-duration anomaly, diagnosing its cause, and applying a documented fix
- **Star schema modeling** — separating facts from dimensions in Power BI
- **DAX measures** — CALCULATE, DIVIDE, AVERAGE with context filters
- **Thinking about different audiences** — an interactive dashboard for managers who want to explore, a one-page PDF for executives who need to scan
- **Documentation** — writing down methodology choices, data quirks, and reproducibility steps

---

## 📌 About This Project

This is a personal project I built to practice operations analytics workflows end-to-end. I learned a lot working through the real friction points — deciding how to handle the negative durations, figuring out which denominator to use for which metric, and thinking about what a manager vs. an executive would want to see.

Happy to chat about the approach or take feedback — reach me on [LinkedIn](https://www.linkedin.com/in/agrima-m-s/).
