#!/usr/bin/env python3

from core import get_weighted_probabilities, run_simulation, compute_stats


def prompt_float(message, default):
    raw = input(f"  {message} [{default}]: ").strip()
    return float(raw) if raw else default


def prompt_int(message, default):
    raw = input(f"  {message} [{default}]: ").strip()
    return int(raw) if raw else default


def get_inputs():
    print("=== MTT Variance Simulator ===\n")

    buyin = prompt_float("Buy-in ($)", 50)
    roi = prompt_float("Expected ROI (e.g. 0.10 for 10%)", 0.10)
    num_tournaments = prompt_int("Tournaments per sample", 1000)
    samples = prompt_int("Number of samples", 1000)
    starting_bankroll = prompt_float("Starting bankroll ($)", 10000)

    print("\n  Enter prize pool as comma-separated values, highest to lowest.")
    print("  Press Enter to use the default: 2025, 1400, 950, 650, 450, 350, 300")
    raw = input("  Prize pool: ").strip()
    if raw:
        prizes = [float(x.strip()) for x in raw.split(",")]
    else:
        prizes = [2025, 1400, 950, 650, 450, 350, 300]

    prizepool = prizes + [0]

    return buyin, roi, num_tournaments, samples, starting_bankroll, prizepool


def print_results(stats):
    print("\n=== Results ===\n")
    print(f"  EV (mathematical):      ${stats['ev_math']:>12,.2f}")
    print(f"  EV (simulated mean):    ${stats['ev_sim']:>12,.2f}")
    print(f"  Std per tourney (math): ${stats['std_math']:>12,.2f}")
    print(f"  Std (simulated):        ${stats['std_sim']:>12,.2f}")
    print(f"  Best sample run:        ${stats['best']:>12,.2f}")
    print(f"  Worst sample run:       ${stats['worst']:>12,.2f}")
    print(f"\n  ITM probability:  {stats['itm']:.1%}")
    print(f"  Bust probability: {1 - stats['itm']:.1%}")


def main():
    buyin, roi, num_tournaments, samples, starting_bankroll, prizepool = get_inputs()
    probs = get_weighted_probabilities(prizepool, roi, buyin)

    print("\nRunning simulation...")
    results = run_simulation(prizepool, probs, buyin, num_tournaments, samples)

    stats = compute_stats(results, probs, prizepool, buyin, num_tournaments)
    print_results(stats)


if __name__ == "__main__":
    main()
