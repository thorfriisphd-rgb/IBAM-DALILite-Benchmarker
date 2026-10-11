"""Data-driven pair classification for IDB. No protein identifiers are embedded here."""
from __future__ import annotations
import csv
from pathlib import Path


def load_groups(path: str | Path | None) -> dict[str, str]:
    if path is None:
        return {}
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Classification registry not found: {path}")
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or not {'Protein', 'Group'}.issubset(reader.fieldnames):
            raise ValueError("Registry needs Protein and Group columns")
        mapping = {}
        for i, row in enumerate(reader, 2):
            protein, group = row['Protein'].strip(), row['Group'].strip()
            if not protein or not group:
                raise ValueError(f"Empty Protein or Group in registry at line {i}")
            if protein in mapping:
                raise ValueError(f"Duplicate protein {protein!r} in registry")
            mapping[protein] = group
        return mapping


def classify_pair(query: str, subject: str, groups: dict[str, str]) -> str:
    """Return a descriptive class; missing metadata is visible, never guessed."""
    if query not in groups or subject not in groups:
        return 'Unclassified'
    a, b = groups[query], groups[subject]
    if a == b:
        return f'Within: {a}'
    return 'Between: ' + ' / '.join(sorted((a, b)))
