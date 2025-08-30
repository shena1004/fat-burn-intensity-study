# Fat-Burn Intensity Study (Simulation + Study Design)

**Question:**
**Primary comparison: ENERGY-MATCHED ✅**

- ~~Time-matched: Over 8–12 weeks, does ~45 min LISS vs ~15–18 min SIT produce different fat-mass change?~~
- **Energy-matched (selected):** When sessions expend ~300 kcal, does LISS vs SIT change **fat mass** differently?


This repo helps you:
1) Write down your **pre-registration-style plan**.
2) Run a simple **simulation** (synthetic students) for Control / LISS / SIT / Mixed programs.
3) Estimate **effect sizes** + ballpark **sample sizes** *before* designing a real study.

---

## Repo Structure

```
fat-burn-intensity-study/
  README.md
  LICENSE
  .gitignore
  requirements.txt
  /src/
    __init__.py
    model.py        # energy balance + state updates
    simulate.py     # runs cohorts for each arm; saves CSV to data/
    analysis.py     # quick summary + plot
  /data/            # synthetic outputs land here
  /figures/         # plots saved here
  /notebooks/
    README.md       # how to make your own notebook
```

---

## Getting Started (Beginner-Friendly)

### Option A — **No command line** (easiest)
1. Create a GitHub account (if you don’t have one).
2. Click **New repository** → name it `fat-burn-intensity-study` → tick **Add a README** → Create.
3. Click **Add file → Upload files** and upload everything from this starter pack (or just upload the `.zip` and then **Extract** on your machine before uploading files).
4. Commit with a message like: `Add starter simulation scaffold`.

### Option B — Command line (Git)
1. Install Git + Python 3.10+.
2. In Terminal:
   ```bash
   git clone https://github.com/<your-username>/fat-burn-intensity-study.git
   cd fat-burn-intensity-study
   ```
3. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run a quick simulation (Example: 8 weeks, 100 participants per arm):
   ```bash
   python -m src.simulate --weeks 8 --n 100 --arms control liss sit mixed
   ```
6. Summarise + plot:
   ```bash
   python -m src.analysis --input data/results_w8_n100.csv
   ```
7. Commit + push:
   ```bash
   git add .
   git commit -m "Run first simulation, add results"
   git push origin main
   ```

---

## Pre-Registration (Draft Skeleton)

**Primary outcome**: Change in **fat mass** (DEXA preferred; BIA acceptable) at end of study.  
**Hypothesis**: SIT ≈ LISS for fat-mass loss when **energy-matched**; Mixed may be slightly better via adherence.  
**Design**: Parallel-arm RCT, university students (18–25).  
**Arms**: Control, LISS (3–4×45 min/wk @60–65% HRR), SIT (3×/wk; 4–6×30 s hard; session ~12–18 min), Mixed (2 LISS + 1 SIT).  
**Diet**: Maintenance kcal with weekly adjustments; track hunger + steps (NEAT).  
**Duration**: 8–12 weeks.  
**Randomisation**: Stratify by sex and baseline fat%.  
**Analysis**: ANCOVA on end fat mass (covariate baseline); mixed-effects model across weeks; ITT + per-protocol; α=0.05.  
**Exclusions/missing**: Define before unblinding; use multiple imputation if needed.  
**Safety**: PAR-Q screening; supervised sprints; stop rules documented.

---

## Methods Lens (how to judge any “X burns more fat” claim)
1. **Participants** (age, training, context)  
2. **What’s compared?** (time vs energy matched)  
3. **Duration** (acute oxidation != long-term fat loss)  
4. **Outcomes** (DEXA vs body weight)  
5. **Controls** (diet, NEAT, adherence)  
6. **Power/effect size** (is it big enough to matter?)

---

## What the Simulation Does (simple but useful)

- Creates **virtual students** with different RMR, appetite reactivity, NEAT behaviour, and adherence.
- Defines energy from exercise + a small **EPOC** bump after SIT.
- Allows **NEAT compensation** (e.g., fewer steps after tough days).
- Updates fat mass (FM) and fat-free mass (FFM) daily from energy surplus/deficit.
- Saves a CSV summary you can analyse.

> ⚠️ The model is deliberately simple and **not** a physiological gold standard. It’s for *planning*: to see likely effect sizes and n/group *before* any real trial.

---

## First Tasks for You
- Decide whether you’re **time-matching** or **energy-matching**. Update `simulate.py` defaults.
- Run `python -m src.simulate --weeks 8 --n 200` and scan `data/` results.
- Open `src/model.py` and tweak the assumptions (EPOC size, NEAT-comp, adherence). Re-run and see how conclusions shift.
- Write down your final study design in **this README** under “Pre-Registration”. Commit that as its own change.
