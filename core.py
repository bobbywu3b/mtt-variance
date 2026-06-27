import numpy as np


def get_weighted_probabilities(prizepool, roi, buyin):
    prizes = np.array(prizepool[:-1], dtype=float)
    mean_prize = prizes.mean()
    p_itm = min((buyin * (1 + roi)) / mean_prize, 1.0)

    probs = np.full(len(prizes), p_itm / len(prizes))
    return np.append(probs, 1.0 - p_itm)


def run_simulation(prizepool, probs, buyin, num_tournaments, samples):
    rng = np.random.default_rng()
    final_bankrolls = []

    for _ in range(samples):
        outcomes = rng.choice(prizepool, size=num_tournaments, p=probs)
        profit = np.sum(outcomes) - (buyin * num_tournaments)
        final_bankrolls.append(profit)

    return np.array(final_bankrolls)


def generate_prizepool(num_players, buyin, rake_pct, pct_paid):
    total = num_players * buyin * (1 - rake_pct / 100)
    num_paid = max(1, int(num_players * pct_paid / 100))

    if num_paid == 1:
        return [round(total, 2)], round(total, 2), 1

    r = 0.65 + 0.30 * (1 - np.exp(-num_paid / 20))
    weights = np.array([r ** k for k in range(num_paid)])
    weights /= weights.sum()

    prizes = sorted((weights * total).tolist(), reverse=True)
    return [round(p, 2) for p in prizes], round(total, 2), num_paid


def _analytical_buyins(prizepool_arr, probs, buyin):
    mean_payout = np.dot(probs, prizepool_arr)
    roi = (mean_payout - buyin) / buyin
    if roi <= 0:
        return float("inf"), 0.0
    std = np.sqrt(np.dot(probs, (prizepool_arr - mean_payout) ** 2))
    return -np.log(0.05) * std ** 2 / (2 * buyin * roi * buyin), roi


def simulate_risk_of_ruin(prizepool, probs, buyin, n_buyins, num_samples=500, max_tournaments=2000):
    rng = np.random.default_rng()
    outcomes = rng.choice(prizepool, size=(num_samples, max_tournaments), p=probs)
    bankrolls = n_buyins * buyin + np.cumsum(outcomes - buyin, axis=1)
    return float(np.any(bankrolls < buyin, axis=1).mean())


def find_buyins_for_ror(prizepool, probs, buyin, target_ror, num_samples=500, max_tournaments=2000):
    prizepool_arr = np.array(prizepool)
    seed, roi = _analytical_buyins(prizepool_arr, probs, buyin)
    if roi <= 0:
        return float("inf"), 1.0

    lo = max(1, int(seed * 0.25))
    hi = max(int(seed * 3.0), lo + 100)

    for _ in range(12):
        mid = (lo + hi) // 2
        if mid == lo:
            break
        ror = simulate_risk_of_ruin(prizepool, probs, buyin, mid, num_samples, max_tournaments)
        if ror > target_ror:
            lo = mid
        else:
            hi = mid

    final_ror = simulate_risk_of_ruin(prizepool, probs, buyin, hi, num_samples, max_tournaments)
    return hi, final_ror


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
