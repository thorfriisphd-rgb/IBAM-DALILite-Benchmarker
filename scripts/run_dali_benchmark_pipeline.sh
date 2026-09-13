#!/usr/bin/env bash
set -euo pipefail

############################################################
# IBAM / C12orf29 Structural Benchmark Pipeline
# Master orchestrator for DALILite benchmarking
#
# Expected layout:
#
# project_root/
# ├── dali_projects/     (DATASET - run from here)
# │    └── dali_* folders
# │         └── pdb/
# │              *.pdb
# │
# └── scripts/
#      run_dali_benchmark_pipeline.sh
#      run_dalilite_batch.sh
#      parse_dalilite_results.sh
#      make_manuscript_dali_table.py
#      make_manuscript_dali_table_md.py
#
# Usage:
#
# cd dali_projects
# bash ../scripts/run_dali_benchmark_pipeline.sh
#
############################################################

log() {
    echo "[IBAM-DALI] $*"
}

die() {
    echo "[IBAM-DALI ERROR] $*" >&2
    exit 1
}

############################################################
# Resolve directories
############################################################

ROOT_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$ROOT_DIR")"
RUN_ID="$(date +'%Y%m%d_%H%M%S')"
RUN_DIR="${PROJECT_ROOT}/dali_batch_runs/${RUN_ID}"

log "ROOT_DIR     = ${ROOT_DIR}"
log "SCRIPT_DIR   = ${SCRIPT_DIR}"
log "RUN_ID       = ${RUN_ID}"
log "RUN_DIR      = ${RUN_DIR}"

############################################################
# Sanity checks
############################################################

log "Checking dataset structure"

shopt -s nullglob
projects=(dali_*)
[[ ${#projects[@]} -gt 0 ]] || die "No dali_* directories found."

for d in "${projects[@]}"; do
    [[ -d "$d/pdb" ]] || die "$d missing pdb directory"

    pdb_count=$(ls "$d/pdb/"*.pdb 2>/dev/null | wc -l)

    if [[ "$pdb_count" -ne 2 ]]; then
        die "$d must contain exactly two pdb files"
    fi
done

log "Dataset validation passed (${#projects[@]} comparisons)"

############################################################
# Prepare run directory
############################################################

mkdir -p "$RUN_DIR"

############################################################
# Run DALILite batch comparisons
############################################################

log "Running DALILite comparisons"

bash "${SCRIPT_DIR}/run_dalilite_batch.sh" \
    "$ROOT_DIR" \
    "$RUN_DIR"

############################################################
# Parse DALILite output
############################################################

RESULTS_DIR="${RUN_DIR}/results"
mkdir -p "$RESULTS_DIR"

SUMMARY_TSV="${RESULTS_DIR}/dali_summary.tsv"
MANUSCRIPT_TSV="${RESULTS_DIR}/dali_manuscript_table.tsv"
MANUSCRIPT_MD="${RESULTS_DIR}/dali_manuscript_table.md"

log "Parsing DALILite output"

bash "${SCRIPT_DIR}/parse_dalilite_results.sh" \
    "$RUN_DIR" \
    "$SUMMARY_TSV"

############################################################
# Generate manuscript tables
############################################################

log "Generating manuscript tables"

python3 "${SCRIPT_DIR}/make_manuscript_dali_table.py" \
    "$SUMMARY_TSV" \
    "$MANUSCRIPT_TSV"

python3 "${SCRIPT_DIR}/make_manuscript_dali_table_md.py" \
    "$SUMMARY_TSV" \
    "$MANUSCRIPT_MD"

echo "-----------------------------------------------------"
echo "DALILite structural benchmark results"
echo "-----------------------------------------------------"

log "Benchmark summary preview"

if [[ -f "$MANUSCRIPT_TSV" ]]; then
    echo
    column -t -s $'\t' "$MANUSCRIPT_TSV"
    echo
else
    log "No manuscript TSV found to preview"
fi

############################################################
# Final report
############################################################

log "Pipeline finished successfully"

log "Results written to:"
echo "  $RESULTS_DIR"

log "Generated files:"
ls -1 "$RESULTS_DIR"

log "DALILite run outputs located in:"
echo "  $RUN_DIR"