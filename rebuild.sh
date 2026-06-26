#!/usr/bin/env bash
set -euo pipefail

echo "==> [1/5] installing python deps"
pip install -q duckdb datasets pillow boto3 pandas

echo "==> [2/5] resetting bucket + catalog"
python scripts/05_reset.py

echo "==> [3/5] landing raw layer (coco + visdrone)"
python scripts/10_land_coco.py
python scripts/11_land_visdrone.py

echo "==> [4/5] building silver + gold"
python scripts/20_build_layers.py

echo "==> [5/5] snapshots after rebuild"
python scripts/40_snapshots.py

echo "DONE. Lakehouse rebuilt from an empty bucket."
