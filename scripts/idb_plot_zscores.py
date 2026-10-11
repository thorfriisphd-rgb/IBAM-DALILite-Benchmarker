#!/usr/bin/env python3
"""Generic IDB horizontal Z-score plot from a classified manuscript TSV.

Required columns: Pair, Class, Z. Class is produced by make_manuscript_dali_table.py.
No known proteins, PDB identifiers, or biological groups are hard-coded.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_tsv', type=Path)
    parser.add_argument('--output', type=Path, default=Path('dali_zscores'))
    args = parser.parse_args()
    df = pd.read_csv(args.input_tsv, sep='\t')
    if df.empty or not {'Pair','Class','Z'}.issubset(df.columns):
        parser.error('Nonempty TSV with Pair, Class and Z columns required')
    if df[['Pair','Class','Z']].isna().any().any():
        parser.error('Empty Pair, Class or Z field')
    df['Z'] = pd.to_numeric(df['Z'], errors='raise')
    if (df['Z'] <= 0).any():
        parser.error('Z-scores must be positive')
    if df['Pair'].duplicated().any():
        parser.error('Duplicate comparison labels')

    within = sorted(c for c in df['Class'].unique() if c.startswith('Within: '))
    between = sorted(c for c in df['Class'].unique() if c.startswith('Between: '))
    other = sorted(set(df['Class']) - set(within) - set(between) - {'Unclassified'})
    if other:
        parser.error(f'Unrecognized comparison classes: {other}')
    palette = plt.get_cmap('tab10')
    colors = {c: palette(i % 10) for i, c in enumerate(within)}
    colors.update({c: '#D38A35' for c in between})
    colors['Unclassified'] = '#888888'
    df = df.sort_values(['Z','Pair'], kind='stable')
    fig, ax = plt.subplots(figsize=(11.5, max(5.5, .4*len(df)+1.6)))
    bars = ax.barh(df['Pair'], df['Z'], color=[colors[c] for c in df['Class']], height=.72)
    ax.bar_label(bars, fmt='%.1f', padding=4, fontsize=9)
    ax.set_xlabel('DALI Z-score')
    ax.set_xlim(0, df['Z'].max()*1.15)
    ax.set_title('DALILite structural comparisons', pad=16)
    ax.grid(axis='x', alpha=.22)
    ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    present = [c for c in within+between+['Unclassified'] if c in set(df['Class'])]
    ax.legend(handles=[Patch(facecolor=colors[c], label=c) for c in present],
              loc='lower right', frameon=False, title='Comparison class', fontsize=8)
    fig.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for ext in ('.png','.pdf','.svg'):
        fig.savefig(args.output.with_suffix(ext), dpi=240, bbox_inches='tight')
    plt.close(fig)
    print(f'Wrote {args.output} (.png, .pdf, .svg)')

if __name__ == '__main__':
    main()
