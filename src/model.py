"""
Simple energy-balance model for virtual students.

This is *not* a physiologically complete model. It's a planning tool to explore
how assumptions (EPOC, NEAT compensation, adherence) change expected effect sizes.
"""
from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class Participant:
    id: int
    sex: str  # 'F' or 'M'
    weight: float  # kg
    fat_mass: float  # kg
    ffm: float  # kg
    rmr: float  # kcal/day
    appetite_reactivity: float  # 0..1 scale (higher => more intake after hard sessions)
    neat_baseline: float  # kcal/day from non-exercise activity
    adherence: float  # 0..1 probability an assigned session actually happens

def estimate_rmr(ffm_kg: float) -> float:
    """Very rough RMR estimate (kcal/day) from FFM."""
    # ~ 22-24 kcal/kg FFM/day; using 23 as a ballpark
    return 23.0 * ffm_kg

def daily_update(p: Participant, protocol: dict, is_session_day: bool, rng: np.random.Generator) -> dict:
    """Update one participant for one day.

    protocol keys (examples):
      - 'session_kcal' (float): energy cost of the session if done
      - 'epoc_kcal' (float): extra kcal in 24h after SIT
      - 'neat_comp' (float): fractional reduction in NEAT on hard days (e.g., 0.05 = -5%)
      - 'diet_kcal' (float): intended intake (maintenance-ish)
      - 'session_type' (str): 'control'|'liss'|'sit'|'mixed'
    """
    # Baseline
    diet_kcal = protocol.get('diet_kcal', p.rmr + p.neat_baseline + 300)  # crude default
    neat = p.neat_baseline
    eat = 0.0
    epoc = 0.0

    did_session = False
    if is_session_day and rng.random() < p.adherence and protocol['session_type'] != 'control':
        did_session = True
        eat = protocol.get('session_kcal', 250.0)
        # NEAT compensation after hard work
        if protocol['session_type'] in ('sit', 'mixed'):
            neat *= (1.0 - protocol.get('neat_comp', 0.05))
            epoc = protocol.get('epoc_kcal', 30.0)

        # Appetite bump for some participants
        diet_kcal += p.appetite_reactivity * (50.0 if protocol['session_type'] in ('sit', 'mixed') else 20.0)

    # Total daily expenditure
    rmr = p.rmr
    tdee = rmr + neat + eat + epoc

    # Energy balance
    balance = diet_kcal - tdee  # positive => surplus
    # Partition: assume 85% of surplus to FM, 15% to FFM; in deficit, 85% from FM, 15% from FFM
    part = 0.85
    kcal_per_kg_fat = 7700.0
    kcal_per_kg_ffm = 1800.0  # very rough; includes glycogen+water dynamics

    if balance >= 0:
        d_fm = (part * balance) / kcal_per_kg_fat
        d_ffm = ((1 - part) * balance) / kcal_per_kg_ffm
    else:
        d_fm = (part * balance) / kcal_per_kg_fat
        d_ffm = ((1 - part) * balance) / kcal_per_kg_ffm

    # Update body comp
    p.fat_mass = max(0.0, p.fat_mass + d_fm)
    p.ffm = max(0.0, p.ffm + d_ffm)
    p.weight = p.fat_mass + p.ffm

    # Update RMR as a function of FFM
    p.rmr = estimate_rmr(p.ffm)

    return {
        'did_session': did_session,
        'diet_kcal': diet_kcal,
        'tdee': tdee,
        'balance': balance,
        'd_fm': d_fm,
        'd_ffm': d_ffm,
        'weight': p.weight,
        'fat_mass': p.fat_mass,
        'ffm': p.ffm,
    }