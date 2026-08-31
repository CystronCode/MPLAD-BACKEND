#!/usr/bin/env bash
# scripts/verify_offline_build.sh
# Comprehensive offline verification script for SIH26102 MEEV

set -e

echo "=================================================================="
echo "  SIH26102 — MEEV (MPLADS Education Ecosystem Validator)"
echo "  OFFLINE REPOSITORY BUILD & VERIFICATION GATE"
echo "=================================================================="

export PYTHONPATH="$(pwd)"

echo "[1/4] Running Schema & Contract Tests..."
pytest tests/contracts -v

echo "[2/4] Running Anomaly Detection & Entity Matcher Tests..."
pytest tests/detection tests/resolution -v

echo "[3/4] Running FastAPI Backend Integration Tests..."
pytest tests/backend -v

echo "[4/4] Running 15-Scenario Adversarial E2E Suite..."
pytest tests/e2e/test_adversarial_suite.py -v

echo "Testing Frontend Build..."
cd frontend
npm run build
cd ..

echo "Running 4-Minute Demo Flow Rehearsal Check..."
python scripts/run_demo_rehearsal.py

echo "=================================================================="
echo "  [SUCCESS] 100% OFFLINE BUILD & VERIFICATION GATES PASSED"
echo "=================================================================="
