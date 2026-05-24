# IBAM DALILite Structural Benchmark

This repository contains the reproducibility pipeline for the structural benchmarking analyses used in the IBAM/C12orf29 study.

C12orf29 is proposed here to encode IBAM (In Between Actin and Myosin), a conserved contractile-system protein exhibiting a deeply conserved actomyosin interaction grammar spanning approximately one billion years of evolution.

The DALILite benchmark framework tests whether IBAM conforms to canonical RNA ligase structural families, an annotation previously proposed in the literature.

The pipeline performs systematic DALILite structural comparisons between:

- canonical RNA ligases
- IBAM vs RNA ligases
- IBAM vs IBAM homologues

The goal is to rigorously test the hypothesis that C12orf29 is structurally related to RNA ligases.
The entire analysis can be reproduced with a single command.

### Repository Structure
```
IBAM_DALILite_benchmark/
│
├── dali_projects/                  # Input dataset (PDB structures and comparison definitions)
│   ├── dali_1S68_vs_5COT/
│   ├── dali_1S68_vs_OaC12/
│   ├── dali_5COT_vs_2HVQ/
│   └── ... (additional comparisons)
│
├── scripts/                        # Pipeline scripts
│   ├── run_dali_benchmark_pipeline.sh
│   ├── run_dalilite_batch.sh
│   ├── parse_dalilite_results.sh
│   ├── make_manuscript_dali_table.py
│   └── make_manuscript_dali_table_md.py
│
└── README.md
```

`dali_projects/` contains the input structures only and should **not be modified**.

##### Pipeline outputs are generated automatically in:
```
dali_batch_runs/
```
## Species and reference-structure origins

The DALILite benchmark includes both C12/IBAM-family structures and canonical RNA ligase reference structures. The table below lists the organismal or source origin of each abbreviation used in the benchmark folder names.

| Abbreviation | Organism / source | Broad lineage | Role in benchmark |
|---|---|---|---|
| Mm | *Mus musculus* | Vertebrate / mammal | C12orf29 / IBAM-family structure |
| Oa | *Ovis aries* | Vertebrate / mammal | C12orf29 / IBAM-family structure |
| Hc | *Hahella chejuensis* | Bacterium / Gammaproteobacteria | C12/IBAM-family structure |
| Ng | *Naegleria gruberi* | Discoba / Heterolobosea | C12/IBAM-family structure |
| Planc | Planctomycetes representative | Bacterium / Planctomycetota | C12/IBAM-family structure |
| 1S68 | Tequatrovirus T4 | Bacteriophage | T4 RNA ligase 2 reference structure |
| 2HVQ | Tequatrovirus T4 | Bacteriophage | Adenylated full-length T4 RNA ligase 2 reference structure |
| 5COT | *Naegleria gruberi* | Discoba / Heterolobosea | RNA ligase reference structure |
| 5D1P | *Methanothermobacter thermautotrophicus* str. Delta H | Archaeon / Euryarchaeota | RNA ligase reference structure |
| 6N67 | *Thermochaetoides thermophila* DSM 1495 | Bacterium / Thermotogota-related lineage | RNA ligase reference structure |


The C12/IBAM-family structures are compared against RNA ligase reference structures to distinguish broad fold-level similarity from specific structural identity with canonical RNA ligases. The benchmark therefore includes both C12-vs-ligase comparisons and ligase-vs-ligase controls.


---

## Requirements

The pipeline requires:

```
Linux or macOS shell
DALILite v5
Python3
```

DALILite must be available in the system `PATH`.

Example installation location:

```
~/DaliLite/DaliLite.v5/bin/dali.pl
```

Add DALILite to the `PATH` if necessary:

```
export PATH="$HOME/DaliLite/DaliLite.v5/bin:$PATH"
```

---

## Running the Benchmark

From the repository root:

```
cd dali_projectsbash ../scripts/run_dali_benchmark_pipeline.sh
```

The pipeline will automatically:

- validate the dataset structure
- run all DALILite pairwise structural comparisons
- parse the results
- generate manuscript-ready summary tables

Runtime on a typical workstation is approximately 1 minute.

---

## Output

Results are written to:

```
dali_batch_runs/results/
```

### Generated files

|File|Description|
|---|---|
|`dali_summary.tsv`|Parsed DALILite output|
|`dali_manuscript_table.tsv`|Formatted table used in the manuscript|
|`dali_manuscript_table.md`|Markdown version of the benchmark table|

A preview of the benchmark results is also printed to the terminal when the pipeline finishes.

---

## Reproducibility

All structural comparisons are explicitly defined in the dataset.

Running the pipeline regenerates the benchmarking table directly from the input structures without manual intervention.

This ensures that the structural benchmark reported in the study can be fully reproduced by any reviewer or reader.

---

## Citation

If you use this repository, please cite the associated IBAM/C12orf29 study and reference this repository directly.

Friis TE. _C12orf29 encodes IBAM (In Between Actin and Myosin), a conserved actomyosin-associated protein exhibiting deeply conserved interaction grammar across eukaryotic evolution._ Manuscript in preparation.

---

## License

MIT License

Copyright (c) Thor Friis

---


## Author

Thor Friis

[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--4132--4912-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0000-0002-4132-4912)

Independent researcher, Bodø, Norway.
PhD in Molecular Biology, Queensland University of Technology (QUT).



