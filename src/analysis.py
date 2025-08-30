import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def summarise(input_csv: str) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    # End-of-study rows only
    max_day = df['day'].max()
    end = df[df['day'] == max_day].copy()
    summary = end.groupby('arm')[['weight','fat_mass','ffm']].agg(['mean','std','count'])
    # Flatten columns
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    return summary.reset_index()

def plot_fat_mass(df: pd.DataFrame, outfile: str):
    plt.figure()
    plt.bar(df['arm'], df['fat_mass_mean'], yerr=df['fat_mass_std'])
    plt.ylabel('Fat Mass (kg) — mean ± SD at end')
    plt.title('End-of-Study Fat Mass by Arm')
    Path(outfile).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Saved figure: {outfile}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=str, required=True, help='CSV from src.simulate')
    args = ap.parse_args()

    summary = summarise(args.input)
    print(summary.to_string(index=False))

    outpng = str(Path('figures') / ('fat_mass_' + Path(args.input).stem + '.png'))
    plot_fat_mass(summary, outpng)

if __name__ == '__main__':
    main()