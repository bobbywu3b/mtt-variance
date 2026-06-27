# MTT Variance Simulator

An interactive tool for modeling the financial outcomes of multi-table poker tournament (MTT) play. Enter your expected ROI, field size, and buy-in to simulate thousands of tournament samples and understand the variance and bankroll requirements you're actually facing.

## Features

- **Monte Carlo simulation** — runs thousands of tournament samples to show the realistic distribution of outcomes over a given sample size
- **Bankroll calculator** — finds the minimum number of buy-ins needed to stay below your chosen risk-of-ruin threshold (1%, 5%, 10%, or custom)
- **Prize pool generator** — builds a realistic, top-heavy payout structure from field size, rake, and percentage of players paid
- **Charts & stats** — profit distribution histogram, finish probability breakdown, percentile table, and a side-by-side comparison across all risk profiles

## Usage

Set your parameters in the sidebar:

| Parameter | Description |
|---|---|
| Buy-in | Cost to enter each tournament |
| Expected ROI | Your edge as a percentage of the buy-in |
| Tournaments per sample | How many tournaments in one run |
| Number of samples | How many independent runs to simulate |
| Number of players | Field size |
| Rake | House fee as a percentage of the prize pool |
| Players paid | Percentage of the field that cashes |

Click **Run Simulation** to see results.

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Stack

- [Streamlit](https://streamlit.io) — UI
- [NumPy](https://numpy.org) — simulation and statistics
- [Matplotlib](https://matplotlib.org) — charts
