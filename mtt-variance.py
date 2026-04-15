#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# inputs
num_players = 53
buyin = 150
rake = 25/150
roi = 0.2
num_tournaments = 10
samples = 1
starting_bankroll = 10000

prizepool = [2025, 1400, 950, 650, 450, 350, 300, 0]

prob_cash = buyin * (roi + 1) / sum(prizepool)
prob_bust = 1 - prob_cash * (len(prizepool) - 1)

probabilities = [prob_cash] * (len(prizepool) - 1) + [prob_bust]

def run_simulation():
    rng = np.random.default_rng()
    final_bankrolls = []

    for _ in range(samples):
        outcomes = rng.choice(prizepool, size=num_tournaments, p=probabilities)
        print(outcomes)

        profit = np.sum(outcomes) - (buyin * num_tournaments)
        final_bankrolls.append(profit)

    return np.array(final_bankrolls)

results = run_simulation()
print(results)
