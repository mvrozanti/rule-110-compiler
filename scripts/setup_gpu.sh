#!/usr/bin/env bash
# Sets up a CUDA-enabled venv for core/rule110_gpu.py.
#
# Why a venv: nixpkgs `cudaSupport = true` compiles cudatoolkit + cupy
# from source in /tmp (tmpfs), which OOMs a 32GB machine. cupy ships
# prebuilt wheels for CUDA 12.x; pip-installing those is faster and uses
# zero RAM during build.
#
# Usage:
#   bash scripts/setup_gpu.sh
#   source .venv-gpu/bin/activate
#   python -m pytest tests/test_rule110_gpu.py
#   python scripts/bench_gpu.py

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${REPO_ROOT}/.venv-gpu"

# NixOS: pip-installed wheels link against libstdc++/libgcc which aren't
# in default ld paths. Resolve once at setup time and write into the
# venv's activate script so callers don't need to remember.
NIX_GCC_LIB="$(nix eval --raw --impure --expr 'with import (builtins.getFlake "github:NixOS/nixpkgs/nixos-unstable") {system="x86_64-linux";}; "${stdenv.cc.cc.lib}/lib"')"
NIX_ZLIB_LIB="$(nix eval --raw --impure --expr 'with import (builtins.getFlake "github:NixOS/nixpkgs/nixos-unstable") {system="x86_64-linux";}; "${zlib}/lib"')"
NVIDIA_LIB="/run/opengl-driver/lib"

if [[ ! -d "${VENV}" ]]; then
  echo "creating ${VENV} ..."
  python3 -m venv "${VENV}"
fi

# Inject LD_LIBRARY_PATH into the venv's activate script so any
# subsequent `source .venv-gpu/bin/activate` Just Works.
LDLP_LINE="export LD_LIBRARY_PATH=\"${NIX_GCC_LIB}:${NIX_ZLIB_LIB}:${NVIDIA_LIB}:\${LD_LIBRARY_PATH:-}\""
if ! grep -qF "${LDLP_LINE}" "${VENV}/bin/activate"; then
  printf '\n# nix-on-linux fix-up (libstdc++, zlib, nvidia driver libs)\n%s\n' "${LDLP_LINE}" >> "${VENV}/bin/activate"
fi

# shellcheck disable=SC1091
source "${VENV}/bin/activate"

python -m pip install --quiet --upgrade pip
python -m pip install --quiet numpy pytest
python -m pip install --quiet -e "${REPO_ROOT}"

# CuPy: pick the wheel matching the installed CUDA major.
CUDA_MAJOR="$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | awk -F. '{print $1}')"
case "${CUDA_MAJOR}" in
  535|545|550|555|560|570|580|590|595)
    PKG="cupy-cuda12x"
    ;;
  *)
    echo "warning: unrecognized nvidia driver major '${CUDA_MAJOR}'; defaulting to cupy-cuda12x"
    PKG="cupy-cuda12x"
    ;;
esac

python -m pip install --quiet "${PKG}"

# CuPy wheels link against CUDA runtime libs which aren't bundled. Pull
# them as PyPI wheels (no compile, ~200MB total). Without these, the
# first CuPy kernel raises DynamicLibNotFoundError on libnvrtc.
python -m pip install --quiet \
  nvidia-cuda-runtime-cu12 \
  nvidia-cuda-nvrtc-cu12 \
  nvidia-cublas-cu12 \
  nvidia-cusolver-cu12 \
  nvidia-cusparse-cu12 \
  nvidia-cufft-cu12 \
  nvidia-curand-cu12 \
  nvidia-nvjitlink-cu12

python - <<'PY'
import cupy as cp
dev = cp.cuda.Device()
print(f"cupy {cp.__version__} ok | device {cp.cuda.runtime.getDevice()} | compute {dev.compute_capability} | free {dev.mem_info[0]/2**30:.1f} GiB")
PY

echo "done. activate with: source .venv-gpu/bin/activate"
