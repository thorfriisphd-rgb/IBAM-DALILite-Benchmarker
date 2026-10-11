#!/usr/bin/env python3
"""Make manuscript Markdown table from raw DALI summary, including comparison classes."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from idb_classification import classify_pair, load_groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_summary_tsv', type=Path)
    parser.add_argument('output_md', type=Path)
    parser.add_argument('--classes', type=Path, help='TSV with Protein and Group columns')
    args = parser.parse_args()
    groups = load_groups(args.classes)
    lines = ['| Pair | Class | Z | RMSD | lali | %ID |', '|---|---|---:|---:|---:|---:|']
    with args.input_summary_tsv.open(newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        required = {'query','subject','z','rmsd','lali','pid'}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            parser.error(f'Raw summary must contain {sorted(required)}')
        for row in reader:
            q, s = row['query'].strip(), row['subject'].strip()
            fields = [f'{q} vs {s}', classify_pair(q, s, groups), row['z'], row['rmsd'], row['lali'], row['pid']]
            lines.append('| ' + ' | '.join(str(value).replace('|', r'\|') for value in fields) + ' |')
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text('\n'.join(lines)+'\n')
    print(f'Wrote: {args.output_md}')

if __name__ == '__main__':
    main()
