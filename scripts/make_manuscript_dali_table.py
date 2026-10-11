#!/usr/bin/env python3
"""Make manuscript TSV from raw DALI summary; optional generic protein-group registry."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
from idb_classification import classify_pair, load_groups


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_summary_tsv', type=Path)
    parser.add_argument('output_tsv', type=Path)
    parser.add_argument('--classes', type=Path, help='TSV with Protein and Group columns')
    args = parser.parse_args()
    groups = load_groups(args.classes)
    with args.input_summary_tsv.open(newline='') as stream:
        source = csv.DictReader(stream, delimiter='\t')
        required = {'query','subject','z','rmsd','lali','pid'}
        if not source.fieldnames or not required.issubset(source.fieldnames):
            parser.error(f'Raw summary must contain {sorted(required)}')
        rows = []
        for row in source:
            query, subject = row['query'].strip(), row['subject'].strip()
            rows.append({'Pair': f'{query} vs {subject}',
                         'Class': classify_pair(query, subject, groups),
                         'Z':row['z'], 'RMSD':row['rmsd'],
                         'lali':row['lali'], '%ID':row['pid']})
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['Pair','Class','Z','RMSD','lali','%ID'], delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote: {args.output_tsv} ({len(rows)} comparisons)')

if __name__ == '__main__':
    main()
