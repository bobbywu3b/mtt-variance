import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from core import (
    get_weighted_probabilities,
    run_simulation,
    compute_stats,
    find_buyins_for_ror,
    generate_prizepool,
)

st.set_page_config(page_title="MTT Variance Simulator", layout="wide")

RISK_PROFILES = {
    "Low":    {"ror": 0.01},
    "Medium": {"ror": 0.05},
    "High":   {"ror": 0.10},
    "Custom": {"ror": None},
}

if "ror" not in st.session_state:
    st.title("MTT Variance Simulator")
    st.markdown("### What's your risk tolerance?")
    st.markdown(
        "We'll use this to calculate the **number of buy-ins** you need in your bankroll "
        "to stay within your comfort zone over the long run."
    )
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    chosen = None

    with col1:
        st.markdown("#### Low Risk")
        st.markdown("**1% risk of ruin**")
        st.caption("Very conservative — built for long-term safety and minimal bust risk.")
        if st.button("Select Low", use_container_width=True, type="primary"):
            chosen = ("Low", 0.01)

    with col2:
        st.markdown("#### Medium Risk")
        st.markdown("**5% risk of ruin**")
        st.caption("Balanced approach — suits most recreational and semi-pro players.")
        if st.button("Select Medium", use_container_width=True, type="primary"):
            chosen = ("Medium", 0.05)

    with col3:
        st.markdown("#### High Risk")
        st.markdown("**10% risk of ruin**")
        st.caption("Aggressive — accepts more variance in exchange for a leaner bankroll.")
        if st.button("Select High", use_container_width=True, type="primary"):
            chosen = ("High", 0.10)

    with col4:
        st.markdown("#### Custom")
        st.markdown("**Your own threshold**")
        st.caption("Define exactly how much ruin risk you're willing to accept.")
        custom_pct = st.number_input(
            "Risk of ruin (%)", min_value=0.1, max_value=49.9, value=5.0, step=0.1,
            key="custom_pct_input", label_visibility="collapsed"
        )
        if st.button("Select Custom", use_container_width=True):
            chosen = ("Custom", custom_pct / 100)

    if chosen:
        st.session_state["profile_name"] = chosen[0]
        st.session_state["ror"] = chosen[1]
        st.rerun()

    st.stop()

profile_name = st.session_state["profile_name"]
ror = st.session_state["ror"]
ror_pct_str = f"{ror:.1%}"

st.title("MTT Variance Simulator")
st.markdown(f"Risk profile: **{profile_name}** ({ror_pct_str} risk of ruin)")
if st.button("Change Risk Profile", type="secondary"):
    del st.session_state["ror"]
    del st.session_state["profile_name"]
    st.rerun()

st.divider()

with st.sidebar:
    st.header("Parameters")

    buyin = st.number_input("Buy-in ($)", min_value=1.0, value=100.0, step=10.0)
    roi_pct = st.slider("Expected ROI (%)", min_value=-50, max_value=200, value=10, step=1)
    roi = roi_pct / 100

    num_tournaments = st.number_input(
        "Tournaments per sample", min_value=10, value=1000, step=100
    )
    samples = st.number_input("Number of samples", min_value=100, value=1000, step=100)

    st.subheader("Tournament Field")
    num_players = st.number_input("Number of players", min_value=2, value=100, step=10)
    rake_pct = st.slider("Rake (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5)
    pct_paid = st.slider("Players paid (%)", min_value=5, max_value=40, value=15, step=1)

    run_btn = st.button("Run Simulation", type="primary", use_container_width=True)

prizes, total_prize_pool, num_paid = generate_prizepool(
    int(num_players), buyin, rake_pct, pct_paid
)
prizepool = prizes + [0.0]

with st.expander(
    f"Prize pool — {num_paid} spots paid, total ${total_prize_pool:,.0f}",
    expanded=False,
):
    pct_of_pool = [p / total_prize_pool * 100 for p in prizes]
    place_labels = [f"{i+1}{'st' if i==0 else 'nd' if i==1 else 'rd' if i==2 else 'th'}" for i in range(num_paid)]
    pool_data = {
        "Place": place_labels,
        "Payout": [f"${p:,.2f}" for p in prizes],
        "% of pool": [f"{pct:.1f}%" for pct in pct_of_pool],
    }
    st.table(pool_data)

st.divider()

if run_btn:
    probs = get_weighted_probabilities(prizepool, roi, buyin)

    with st.spinner("Running simulation..."):
        results = run_simulation(
            prizepool, probs, buyin, int(num_tournaments), int(samples)
        )

    stats = compute_stats(results, probs, prizepool, buyin, int(num_tournaments))

    st.subheader("Bankroll Requirement")
    if roi <= 0:
        st.warning("Bankroll requirement is undefined for zero or negative ROI.")
    else:
        with st.spinner("Simulating risk of ruin…"):
            n_buyins, actual_ror = find_buyins_for_ror(prizepool, probs, buyin, ror)

        bankroll_needed = n_buyins * buyin
        br1, br2, br3, br4 = st.columns(4)
        br1.metric("Risk Profile", f"{profile_name} ({ror_pct_str})")
        br2.metric("Buy-ins Required", f"{n_buyins:,}")
        br3.metric("Bankroll Required", f"${bankroll_needed:,.0f}")
        br4.metric("Simulated RoR", f"{actual_ror:.1%}")

        with st.expander("Compare all profiles"):
            rows = []
            for pname, pdata in RISK_PROFILES.items():
                r = ror if pname == "Custom" else pdata["ror"]
                if r is None:
                    continue
                bn, bn_ror = find_buyins_for_ror(prizepool, probs, buyin, r)
                rows.append({
                    "Profile": f"{pname} ({r:.1%})",
                    "Buy-ins Required": f"{bn:,}",
                    "Bankroll Required": f"${bn * buyin:,.0f}",
                    "Simulated RoR": f"{bn_ror:.1%}",
                })
            st.table(rows)

    st.divider()

    st.subheader("Simulation Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EV (mathematical)", f"${stats['ev_math']:,.0f}")
    c2.metric("EV (simulated)", f"${stats['ev_sim']:,.0f}", f"{stats['ev_sim'] - stats['ev_math']:+,.0f} vs math")
    c3.metric("ITM Probability", f"{stats['itm']:.1%}")
    c4.metric("Std Dev / tourney", f"${stats['std_math']:,.0f}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Best run", f"${stats['best']:,.0f}")
    c6.metric("Worst run", f"${stats['worst']:,.0f}")
    c7.metric("Std Dev (simulated)", f"${stats['std_sim']:,.0f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Profit Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(results, bins=60, color="#4C72B0", edgecolor="white", linewidth=0.4)
        ax.axvline(results.mean(), color="#DD4444", linestyle="--", linewidth=1.2, label=f"Mean (${results.mean():,.0f})")
        ax.axvline(0, color="#888888", linestyle="--", linewidth=1.0, label="Break even")
        ax.set_xlabel("Profit ($)")
        ax.set_ylabel("Frequency")
        ax.legend(fontsize=9)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        plt.xticks(rotation=20, ha="right")
        fig.tight_layout()
        st.pyplot(fig)

    with col_right:
        st.subheader("Finish Probabilities")
        display_prizes = prizes[:10]
        display_probs = list(probs[:10]) + [probs[-1]]
        labels = [f"${int(p):,}" for p in display_prizes] + ["Bust"]
        if len(prizes) > 10:
            labels[-2] = f"${int(prizes[9]):,}+"
        colors = ["#4C72B0"] * len(display_prizes) + ["#DD4444"]
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(labels, display_probs, color=colors, edgecolor="white", linewidth=0.4)
        ax2.set_ylabel("Probability")
        ax2.set_xlabel("Finish / Payout")
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1%}"))
        for bar, prob in zip(bars, display_probs):
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(display_probs) * 0.01,
                f"{prob:.2%}",
                ha="center", va="bottom", fontsize=7,
            )
        plt.xticks(rotation=20, ha="right")
        fig2.tight_layout()
        st.pyplot(fig2)

    st.subheader("Percentile Breakdown")
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    pct_values = np.percentile(results, percentiles)
    pct_data = {
        "Percentile": [f"{p}th" for p in percentiles],
        "Profit": [f"${v:,.0f}" for v in pct_values],
    }
    st.table(pct_data)
