#!/bin/bash
# Package_Scan - Integrated Static Analysis Toolset

# ================= Configuration =================
ROOT_DIR="/home/capstone/Desktop/root"                # Root directory containing projects
OUT_BASE_DIR="/home/capstone/Desktop/code/results"    # Output directory for all results
SEMGREP_CONFIG="/home/capstone/Desktop/SEAM/semgrep-rules/c"   # Path to Semgrep custom rules
CLANG_CHECKS="*"                                       # Clang-Tidy check rules
# ==================================================

# Create the output directory if it doesn't exist
mkdir -p "$OUT_BASE_DIR"

# Iterate over all projects in the root directory
for PROJECT_DIR in "$ROOT_DIR"/*; do
  if [[ -d "$PROJECT_DIR" ]]; then
    PROJECT_NAME=$(basename "$PROJECT_DIR")
    echo "Processing project: $PROJECT_NAME"
  
    OUTPUT_DIR="$OUT_BASE_DIR/$PROJECT_NAME"
    mkdir -p "$OUTPUT_DIR"

    echo "[1/5] Running Cppcheck..."
    cppcheck --enable=all --inconclusive --quiet --xml \
      "$PROJECT_DIR" 2> "$OUTPUT_DIR/cppcheck.xml"

    # [2/5] Run Flawfinder
    echo "[2/5] Running Flawfinder..."
    
    FLAWFINDER_LOG="$OUTPUT_DIR/flawfinder.log"
    FLAWFINDER_HTML="$OUTPUT_DIR/flawfinder_report.html"

    # Preprocess: Convert non-UTF-8 C files to UTF-8
    find "$PROJECT_DIR" -type f -name '*.c' -exec bash -c '
      for f; do
        if ! iconv -f utf-8 -t utf-8 "$f" > /dev/null 2>&1; then
          echo "🛠️ Converting encoding: $f"
          iconv -f ISO-8859-1 -t UTF-8 "$f" -o "$f.utf8" && mv "$f.utf8" "$f"
        fi
      done
    ' bash {} +

    BASE_OPTS=(
        --quiet        # Suppress progress output
        --context      # Show code context
        --columns      # Show column numbers
        --dataonly     # Output essential data only
    )

    RISK_LEVEL=2  # Minimum issue level to report (1-5)

    # Generate HTML report
    if ! flawfinder "${BASE_OPTS[@]}" \
        --html --neverignore \
        --minlevel=$RISK_LEVEL \
        --error-level=5 \
        "$PROJECT_DIR" > "$FLAWFINDER_HTML" 2> "$FLAWFINDER_LOG"; then

        if grep -q "No hits found" "$FLAWFINDER_LOG"; then
            echo "No security issues found by Flawfinder"
        else
            echo "Flawfinder error - see log: $FLAWFINDER_LOG"
            grep -E 'ERROR|WARNING' "$FLAWFINDER_LOG" | head -n 5 > "$OUTPUT_DIR/flawfinder_errors.txt"
        fi
    fi

    # Generate simplified text report
    flawfinder "${BASE_OPTS[@]}" \
        --singleline \
        --minlevel=1 \
        "$PROJECT_DIR" > "$OUTPUT_DIR/flawfinder.txt"

    # Generate CSV report
    flawfinder --csv "$PROJECT_DIR" > "$OUTPUT_DIR/flawfinder.csv"

    # [3/5] Run Clang Static Analyzer
    echo "[3/5] Running Clang Static Analyzer..."
    CSA_OUTPUT="$OUTPUT_DIR/clang-sa"
    mkdir -p "$CSA_OUTPUT"

    if [[ -f "$PROJECT_DIR/Makefile" ]]; then
      (cd "$PROJECT_DIR" && scan-build -o "$CSA_OUTPUT" make clean all)
    else
      echo "⚠️ No Makefile found, trying to generate one..."

      if [[ -f "$PROJECT_DIR/Makefile.am" ]]; then
        echo "Found Makefile.am, using Autotools..."
        (cd "$PROJECT_DIR" && autoreconf -fi && ./configure && make clean all)
        if [[ -f "$PROJECT_DIR/Makefile" ]]; then
          scan-build -o "$CSA_OUTPUT" make -C "$PROJECT_DIR" clean all
        else
          echo "Autotools failed to generate Makefile"
        fi
      elif [[ -f "$PROJECT_DIR/Makefile.dist" ]]; then
        echo "Found Makefile.dist, copying to Makefile..."
        cp "$PROJECT_DIR/Makefile.dist" "$PROJECT_DIR/Makefile"
        scan-build -o "$CSA_OUTPUT" make -C "$PROJECT_DIR" clean all
      else
        echo "Creating temporary Makefile to compile all C files..."
        echo -e "CC=gcc\nCFLAGS=-Wall -Wextra\nall:\n\t\$(CC) \$(CFLAGS) *.c -o output" > "$PROJECT_DIR/Makefile"
        scan-build -o "$CSA_OUTPUT" make -C "$PROJECT_DIR" clean all
      fi
    fi

    # [4/5] Run Clang-Tidy
    echo "[4/5] Running Clang-Tidy..."
    find "$PROJECT_DIR" -type f \( -name "*.c" -o -name "*.h" \) -exec \
      clang-tidy {} -checks="$CLANG_CHECKS" -- -I"$PROJECT_DIR" \; \
      > "$OUTPUT_DIR/clang-tidy.txt" 2>&1

    # [5/5] Run Semgrep
    echo "[5/5] Running Semgrep..."

    SEMGREP_JSON="${OUTPUT_DIR}/semgrep.json"
    SEMGREP_LOG="${OUTPUT_DIR}/semgrep_scan.log"

    echo "Scanning directory: $PROJECT_DIR"
    ls -l "$PROJECT_DIR"

    if [[ ! -d "$SEMGREP_CONFIG" ]]; then
        echo "[WARN] Custom Semgrep config not found at $SEMGREP_CONFIG" | tee -a "$SEMGREP_LOG"
        SEMGREP_CONFIG="p/default"
        echo "Using fallback Semgrep config: $SEMGREP_CONFIG" | tee -a "$SEMGREP_LOG"
    fi

    semgrep_cmd=(
      semgrep scan
      --include '**/*.c' --include '**/*.h'
      --config "$SEMGREP_CONFIG"
      --scan-unknown-extensions
      --json
      --output "$SEMGREP_JSON"
    )

    if ! "${semgrep_cmd[@]}" "$PROJECT_DIR" > >(tee -a "$SEMGREP_LOG") 2>&1; then
        echo "[ERROR] Semgrep scan failed with config: $SEMGREP_CONFIG"
        echo "Attempting fallback with default rules..."
        semgrep scan --config "p/default" \
                    --no-git-ignore \
                    --scan-unknown-extensions \
                    --json \
                    --output "${OUTPUT_DIR}/semgrep_fallback.json" \
                    "$PROJECT_DIR"
    fi

    if [[ -f "$SEMGREP_JSON" ]] && jq empty "$SEMGREP_JSON" &> /dev/null; then
        echo "Semgrep results saved to: $SEMGREP_JSON"
        jq '.results[] | "\(.extra.severity): \(.path):\(.start.line) - \(.extra.message)"' \
        "$SEMGREP_JSON" > "${OUTPUT_DIR}/semgrep_summary.txt"
    else
        echo "[WARN] No valid Semgrep results generated"
        echo "Check detailed log: $SEMGREP_LOG"
    fi
  fi
done

echo "All project scans completed! Results directory: $OUT_BASE_DIR"
