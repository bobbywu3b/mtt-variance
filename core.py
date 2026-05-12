import numpy as np


def get_weighted_probabilities(prizepool, roi, buyin):
    prizes = np.array(prizepool[:-1], dtype=float)

    # Lower prizes (worse finishes near the bubble) are more likely than deeper runs.
    # Weight inversely by payout so min-cash has highest probability.
    base_weights = 1.0 / prizes
    base_weights /= base_weights.sum()

    req_avg_return = buyin * (1 + roi)
    weighted_payout_sum = np.sum(base_weights * prizes)
    p_itm = req_avg_return / weighted_payout_sum

    probs = base_weights * p_itm
    prob_bust = 1 - probs.sum()

    return np.append(probs, prob_bust)


def run_simulation(prizepool, probs, buyin, num_tournaments, samples):
    rng = np.random.default_rng()
    final_bankrolls = []

    for _ in range(samples):
        outcomes = rng.choice(prizepool, size=num_tournaments, p=probs)
        profit = np.sum(outcomes) - (buyin * num_tournaments)
        final_bankrolls.append(profit)

    return np.array(final_bankrolls)


def generate_prizepool(num_players, buyin, rake_pct, pct_paid):
    """
    Build a geometric-decay payout structure from field parameters.

    Returns (prizes, total_prize_pool, num_paid) where prizes is a list of
    payouts in descending order (excluding the 0 bust outcome).
    """
    total = num_players * buyin * (1 - rake_pct / 100)
    num_paid = max(1, int(num_players * pct_paid / 100))

    if num_paid == 1:
        return [round(total, 2)], round(total, 2), 1

    # Decay ratio scales toward 1 as field grows, producing realistic top-heavy
    # structures for small fields and flatter ones for large fields.
    r = 0.65 + 0.30 * (1 - np.exp(-num_paid / 20))
    weights = np.array([r ** k for k in range(num_paid)])
    weights /= weights.sum()

    prizes = sorted((weights * total).tolist(), reverse=True)
    return [round(p, 2) for p in prizes], round(total, 2), num_paid


def compute_required_buyins(std_math, buyin, roi, ror):
    """RoR = exp(-2 * mu * B / sigma^2) solved for B, then divided by buyin."""
    if roi <= 0 or ror <= 0 or ror >= 1:
        return float("inf")
    mu = buyin * roi
    sigma2 = std_math ** 2
    bankroll = -np.log(ror) * sigma2 / (2 * mu)
    return bankroll / buyin


def compute_stats(results, probs, prizepool, buyin, num_tournaments):
    prizepool_arr = np.array(prizepool)
    ev_math = (np.dot(probs, prizepool_arr) - buyin) * num_tournaments
    mean_payout = np.dot(probs, prizepool_arr)
    std_math = np.sqrt(np.dot(probs, (prizepool_arr - mean_payout) ** 2))
    return {
        "ev_math": ev_math,
        "ev_sim": results.mean(),
        "std_math": std_math,
        "std_sim": results.std(),
        "best": results.max(),
        "worst": results.min(),
        "itm": 1 - probs[-1],
    }
