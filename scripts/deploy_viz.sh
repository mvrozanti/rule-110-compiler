#!/usr/bin/env bash
# Publishes viz/ to rule110.mvr.ac.
#
# Prerequisites (one-time):
#   1. Compose slot exists on the VPS at /home/opc/rule110/
#      (see /etc/nixos/mandragora/nix/hosts/mandragora-vps/compose/rule110/README.md
#      for first-time bring-up).
#   2. DNS rule110.mvr.ac points at the VPS (wildcard *.mvr.ac handles it).
#
# Usage:
#   bash scripts/deploy_viz.sh
#
# After: nginx in the rule110 container serves the new files immediately,
# no restart needed.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIZ_DIR="${REPO_ROOT}/viz"
TARGET="${RULE110_DEPLOY_TARGET:-opc@mandragora-vps:/home/opc/rule110/static/}"

if [[ ! -f "${VIZ_DIR}/index.html" ]]; then
  echo "error: ${VIZ_DIR}/index.html not found"
  exit 1
fi

echo "deploying ${VIZ_DIR}/ -> ${TARGET}"
rsync -av --delete "${VIZ_DIR}/" "${TARGET}"

echo "done. https://rule110.mvr.ac/"
