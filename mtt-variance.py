import numpy as np
import matplotlib.pyplot as plt

# inputs
num_players = 1040
buyin = 400
rake = 55 / 400
roi = 0.2
num_tournaments = 1000
samples = 1000
starting_bankroll = 10000

prizepool = [72000, 45400, 29450, 20350, 15740, 12600, 10750, 9000, 7400, 
    5800, 5800, 4400, 4400, 3200, 3200, 2400, 2400, 2400] + [1800] * 9 + [1400] * 9
    + [1200] * 9 + [1100] * 18 + [1000] * 18 + [900] * 9 + [850] * 9 + [800] * 6

prob_cashing = (1 / num_players) * (1 + roi)
prob_no_cash = 1 - (len(prizeool) * probability_cashing)

all_probs = [prob_cashing] * len(prizepool) + [prob_no_cash]
all_payouts = prizepool + [0]