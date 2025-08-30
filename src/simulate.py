import argparse, csv, math
from pathlib import Path
import numpy as np
import pandas as pd
from .model import Participant, estimate_rmr, daily_update

def make_participant(pid: int, rng: np.random.Generator) -> Participant:
    sex = 'F' if rng.random() < 0.5 else 'M'
    # Baseline body comp distributions (very rough)
    weight = rng.normal(65 if sex=='F' else 78, 8)
    fat_pct = rng.normal(0.30 if sex=='F' else 0.20, 0.05)
    fat_mass = max(5.0, weight * fat_pct)
    ffm = max(30.0, weight - fat_mass)
    rmr = estimate_rmr(ffm)
    appetite = np.clip(rng.normal(0.4, 0.2), 0.0, 1.0)
    neat = rng.normal(500, 120)  # kcal/day
    adher = np.clip(rng.normal(0.9, 0.1), 0.4, 1.0)
    return Participant(pid, sex, weight, fat_mass, ffm, rmr, appetite, neat, adher)

def protocol_for_arm(arm: str, energy_matched: bool = False) -> dict:
    # Defaults roughly time-matched: LISS ~45 min, SIT ~12-18 min with small EPOC
    if arm == 'control':
        return dict(session_type='control', session_kcal=0.0, epoc_kcal=0.0, neat_comp=0.0)
    if arm == 'liss':
        return dict(session_type='liss', session_kcal=250.0, epoc_kcal=0.0, neat_comp=0.0)
    if arm == 'sit':
        return dict(session_type='sit', session_kcal=170.0, epoc_kcal=40.0, neat_comp=0.05)
    if arm == 'mixed':
        # Will alternate liss/sit inside the loop
        return dict(session_type='mixed', session_kcal=220.0, epoc_kcal=20.0, neat_comp=0.03)
    raise ValueError(f"Unknown arm: {arm}")

def weekly_schedule(arm: str):
    """Return a list of 7 booleans for session days. Defaults to 3 sessions/wk."""
    if arm == 'control':
        return [False, False, False, False, False, False, False]
    # Mon/Wed/Fri as True
    return [True, False, True, False, True, False, False]

def run_sim(weeks: int, n: int, arms: list[str], seed: int = 42, energy_matched: bool = False) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    days = weeks * 7

    for arm in arms:
        prot = protocol_for_arm(arm, energy_matched=energy_matched)
        sched = weekly_schedule(arm)

        # Cohort
        participants = [make_participant(pid=i, rng=rng) for i in range(n)]
        for p in participants:
            # Set diet to maintenance-ish using baseline
            maintenance = p.rmr + p.neat_baseline + 300  # small cushion; tweak as needed
            prot['diet_kcal'] = maintenance

        for p in participants:
            for d in range(days):
                is_session_day = sched[d % 7]
                # Mixed arm alternates: Mon LISS, Wed SIT, Fri LISS (example)
                if arm == 'mixed' and is_session_day:
                    day_idx = d % 7
                    if day_idx in (0, 4):   # Mon/Fri LISS
                        prot_today = dict(prot, session_type='liss', session_kcal=230.0, epoc_kcal=0.0, neat_comp=0.0)
                    else:                   # Wed SIT
                        prot_today = dict(prot, session_type='sit', session_kcal=170.0, epoc_kcal=35.0, neat_comp=0.05)
                else:
                    prot_today = prot

                out = daily_update(p, prot_today, is_session_day, rng)
                rows.append({
                    'arm': arm,
                    'pid': p.id,
                    'day': d+1,
                    'did_session': int(out['did_session']),
                    'weight': out['weight'],
                    'fat_mass': out['fat_mass'],
                    'ffm': out['ffm'],
                    'balance': out['balance'],
                })

    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--weeks', type=int, default=8, help='Number of weeks to simulate')
    ap.add_argument('--n', type=int, default=100, help='Participants per arm')
    ap.add_argument('--arms', nargs='+', default=['control', 'liss', 'sit', 'mixed'],
                    help='Arms to simulate')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--energy-matched', action='store_true', help='Match energy per session instead of time (placeholder)')
    args = ap.parse_args()

    df = run_sim(args.weeks, args.n, args.arms, args.seed, args.energy_matched)

    outpath = Path('data') / f"results_w{args.weeks}_n{args.n}.csv"
    outpath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outpath, index=False)
    print(f"Saved: {outpath}")

if __name__ == '__main__':
    main()