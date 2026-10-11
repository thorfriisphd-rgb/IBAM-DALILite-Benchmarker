#!/usr/bin/env bash
set -euo pipefail

log() {
    echo "[DALI-BATCH] $*"
}

die() {
    echo "[DALI-BATCH ERROR] $*" >&2
    exit 1
}

PROJECTS_DIR="${1:-}"
RUN_DIR="${2:-}"

[[ -n "$PROJECTS_DIR" ]] || die "Missing <projects_dir>"
[[ -n "$RUN_DIR" ]] || die "Missing <run_dir>"

[[ -d "$PROJECTS_DIR" ]] || die "Projects directory not found: $PROJECTS_DIR"
mkdir -p "$RUN_DIR"

log "Projects directory: $PROJECTS_DIR"
log "Run directory: $RUN_DIR"

if command -v dali.pl >/dev/null 2>&1; then
    DALI="$(command -v dali.pl)"
elif [[ -x "$HOME/DaliLite/DaliLite.v5/bin/dali.pl" ]]; then
    DALI="$HOME/DaliLite/DaliLite.v5/bin/dali.pl"
else
    die "DALILite executable 'dali.pl' not found"
fi

log "Using DALILite: $DALI"

alias4() {
    case "$1" in
        1S68)  echo "1S68" ;;
        5COT)  echo "5COT" ;;
        2HVQ)  echo "2HVQ" ;;
        5D1P)  echo "5D1P" ;;
        6N67)  echo "6N67" ;;
        OaC12) echo "OA12" ;;
        HcC12) echo "HC12" ;;
        MmC12) echo "MM12" ;;
        NgC12) echo "NG12" ;;
        Planc) echo "PLN1" ;;
        FvCOT) echo "FVCT" ;;
        *) die "No 4-char DALILite alias defined for: $1" ;;
    esac
}

WORK_BASE="${TMPDIR:-/tmp}/ibdali"
rm -rf "$WORK_BASE"
mkdir -p "$WORK_BASE"

shopt -s nullglob
projects=("${PROJECTS_DIR}"/dali_*)
[[ ${#projects[@]} -gt 0 ]] || die "No dali_* projects found in $PROJECTS_DIR"

for proj in "${projects[@]}"; do
    name="$(basename "$proj")"
    pdb_dir="${proj}/pdb"

    log "Processing $name"
    [[ -d "$pdb_dir" ]] || die "$name missing pdb directory"

    mapfile -t pdbs < <(find "$pdb_dir" -maxdepth 1 -type f -name '*.pdb' | sort)
    [[ ${#pdbs[@]} -eq 2 ]] || die "$name must contain exactly two pdb files"

    pdb1="${pdbs[0]}"
    pdb2="${pdbs[1]}"

    base1="$(basename "$pdb1" .pdb)"
    base2="$(basename "$pdb2" .pdb)"

    id1="$(alias4 "$base1")"
    id2="$(alias4 "$base2")"

    # Short DALILite work dir to avoid path-length failures
    workdir="${WORK_BASE}/${name}"
    rm -rf "$workdir"
    mkdir -p "$workdir/pdb" "$workdir/dat"

    cp -f "$pdb1" "$workdir/pdb/${id1}.pdb"
    cp -f "$pdb2" "$workdir/pdb/${id2}.pdb"

    log "Running DALI: $base1 ($id1) vs $base2 ($id2)"

    pushd "$workdir" >/dev/null

    "$DALI" \
        --pdbfile1 "pdb/${id1}.pdb" --pdbid1 "$id1" \
        --pdbfile2 "pdb/${id2}.pdb" --pdbid2 "$id2" \
        --dat1 ./dat --dat2 ./dat \
        --outfmt summary,alignments \
        --title "$name"

    popd >/dev/null

    # Copy full DALILite outputs back to the persistent run dir
    outdir="${RUN_DIR}/${name}"
    rm -rf "$outdir"
    mkdir -p "$outdir"
    cp -a "$workdir/." "$outdir/"
done

log "All DALILite runs completed"