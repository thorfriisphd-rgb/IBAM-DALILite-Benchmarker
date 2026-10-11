#!/usr/bin/env python3
"""Generic manuscript-ready DALI + optional ChimeraX LaTeX table exporter.

Input DALI TSV: Pair, Class, Z, RMSD, lali, %ID
Optional ChimeraX TSV: Pair, Pruned, Total, GlobalRMSD (and optional PrunedRMSD)
Pair matching is orientation-independent. Unknown classes and absent ChimeraX data
are displayed honestly. No identifiers, families, or benchmark cutoffs hard-coded.
"""
from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from pathlib import Path

COLUMNS = ['Pair','Class','Z','RMSD','lali','%ID']
CHIMERA_COLUMNS = ['Pair', 'Pruned', 'Total', 'GlobalRMSD']

def read_tsv(path, required):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if not reader.fieldnames or not set(required).issubset(reader.fieldnames):
            raise ValueError(f'{path}: required columns {required}; found {reader.fieldnames}')
        rows = list(reader)
    if not rows:
        raise ValueError(f'{path}: empty table')
    return rows

def pairkey(pair):
    parts = [p.strip() for p in pair.split(' vs ')]
    if len(parts) != 2 or not all(parts):
        raise ValueError(f'Invalid Pair {pair!r}; expected "A vs B"')
    if parts[0] == parts[1]:
        raise ValueError(f'Self-comparison {pair!r}')
    return tuple(sorted(parts))

def tex(value):
    # Character-by-character replacement avoids escaping generated macros twice.
    escaped = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
               '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
               '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(escaped.get(c, c) for c in str(value))

def numeric(value, what, *, integer=False):
    try:
        result = int(value) if integer else float(value)
        if not integer and (result != result or result in (float('inf'), float('-inf'))):
            raise ValueError
        if result < 0:
            raise ValueError
        return result
    except (ValueError, TypeError):
        raise ValueError(f'Invalid {what}: {value!r}') from None

def make_table(dali, chimera, caption, label, group, no_resize):
    if not label or any(c in label for c in '\\{}%#&$'):
        raise ValueError('Invalid LaTeX label')
    groups = defaultdict(list)
    for row in dali:
        cls = row.get('Class', '').strip() or 'Unclassified'
        groups[cls].append(row)
    group_names = list(groups)
    if group == 'z':
        for cls in groups:
            groups[cls].sort(key=lambda r: -float(r['Z']))
        group_names.sort(key=lambda cls: -max(float(r['Z']) for r in groups[cls]))
    elif group == 'alpha':
        group_names.sort()
        for cls in groups:
            groups[cls].sort(key=lambda r: r['Pair'])
    # Default uses input order of classes and rows, preserving curated benchmark order.
    lines = [r'\begin{table}[htbp]', r'\centering', r'\small',
             r'\caption{\textbf{' + tex(caption) + r'} DALI metrics report Z-score, '
             r'RMSD, aligned residues and sequence identity. ChimeraX MatchMaker metrics '
             r'report pruned and total atom pairs, coherence (pruned/total) and global RMSD. '
             r'An em dash indicates unavailable ChimeraX measurements; comparison classes '
             r'are supplied by the benchmark metadata, not inferred from DALI.}',
             r'\label{' + label + '}',
             *( [] if no_resize else [r'\resizebox{\textwidth}{!}{%']),
             r'\begin{tabular}{lrrrrrrrr}', r'\toprule',
             r'\textbf{Comparison} & \multicolumn{4}{c}{\textbf{DALI}} & '
             r'\multicolumn{4}{c}{\textbf{ChimeraX}} \\',
             r'\cmidrule(lr){2-5}\cmidrule(lr){6-9}',
             r' & \textbf{Z} & \textbf{RMSD (\AA)} & \textbf{lali} & \textbf{\%ID} & '
             r'\textbf{Pruned} & \textbf{Total} & \textbf{Coherence (\%)} & '
             r'\textbf{Global RMSD (\AA)} \\', r'\midrule']
    for gi, cls in enumerate(group_names):
        if gi:
            lines.append(r'\midrule')
        lines.append(r'\multicolumn{9}{l}{\textit{' + tex(cls) + r'}} \\')
        lines.append(r'\addlinespace[2pt]')
        for row in groups[cls]:
            key = pairkey(row['Pair'])
            if key in chimera:
                cr = chimera[key]
                pr = numeric(cr['Pruned'], 'Pruned', integer=True)
                total = numeric(cr['Total'], 'Total', integer=True)
                if total == 0 or pr > total:
                    raise ValueError(f'Invalid ChimeraX counts for {row["Pair"]}')
                rmsd = numeric(cr['GlobalRMSD'], 'GlobalRMSD')
                match = [str(pr), str(total), f'{100 * pr / total:.1f}', f'{rmsd:.3f}']
            else:
                match = [r'\textemdash'] * 4
            for numcol in ('Z', 'RMSD', 'lali', '%ID'):
                numeric(row[numcol], numcol)
            items = [tex(row['Pair']), *[tex(row[k]) for k in ('Z','RMSD','lali','%ID')], *match]
            lines.append(' & '.join(items) + r' \\')
    lines += [r'\bottomrule', r'\end{tabular}', *( [] if no_resize else ['}%']), r'\end{table}']
    return '\n'.join(lines) + '\n'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('dali_tsv', type=Path)
    p.add_argument('--chimerax', type=Path, help='Optional ChimeraX MatchMaker TSV')
    p.add_argument('--output', type=Path, default=Path('dali_structural_table.tex'))
    p.add_argument('--caption', default='Structural comparison of protein groups')
    p.add_argument('--label', default='tab:structural_comparison')
    p.add_argument('--sort', choices=['input', 'z', 'alpha'], default='z')
    p.add_argument('--no-resize', action='store_true')
    args = p.parse_args()
    try:
        dali = read_tsv(args.dali_tsv, COLUMNS)
        seen = set()
        for row in dali:
            key = pairkey(row['Pair'])
            if key in seen:
                raise ValueError(f'Duplicate DALI pair {row["Pair"]}')
            seen.add(key)
        chimera = {}
        if args.chimerax:
            for row in read_tsv(args.chimerax, CHIMERA_COLUMNS):
                key = pairkey(row['Pair'])
                if key in chimera:
                    raise ValueError(f'Duplicate ChimeraX pair {row["Pair"]}')
                chimera[key] = row
        unused = set(chimera) - seen
        if unused:
            print(f'Warning: {len(unused)} ChimeraX pairs absent from DALI dataset', file=__import__('sys').stderr)
        table = make_table(dali, chimera, args.caption, args.label, args.sort, args.no_resize)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(table, encoding='utf-8')
        fragment = args.output.with_name(args.output.stem + '_fragment.tex')
        # Primary output is Overleaf-ready standalone; fragment is for \input in main manuscript.
        document = (r'\documentclass{article}' + '\n' +
                    r'\usepackage[margin=1in]{geometry}' + '\n' +
                    r'\usepackage{graphicx}' + '\n' +
                    r'\usepackage{booktabs}' + '\n' +
                    r'\begin{document}' + '\n' + table + r'\end{document}' + '\n')
        fragment.write_text(table, encoding='utf-8')
        args.output.write_text(document, encoding='utf-8')
        print(f'Wrote {args.output} and {fragment} ({len(dali)} comparisons, '
              f'{len(seen & set(chimera))} with ChimeraX data)')
    except (OSError, ValueError, KeyError) as e:
        p.exit(2, f'Error: {e}\n')

if __name__ == '__main__':
    main()
