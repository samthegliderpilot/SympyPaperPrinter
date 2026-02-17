#!/usr/bin/env bash
set -euo pipefail

VENV_NAME="${VENV_NAME:-.venv}"
EXTRAS="${EXTRAS:-dev,notebook}"
RECREATE="${RECREATE:-0}"
INSTALL_KERNEL="${INSTALL_KERNEL:-0}"

if [[ ! -f "pyproject.toml" ]]; then
  echo "pyproject.toml not found. Run from a Python project root." >&2
  exit 1
fi

if [[ "$RECREATE" == "1" && -d "$VENV_NAME" ]]; then
  echo "Removing existing venv: $VENV_NAME"
  rm -rf "$VENV_NAME"
fi

if [[ ! -d "$VENV_NAME" ]]; then
  echo "Creating venv: $VENV_NAME"
  python3 -m venv "$VENV_NAME"
else
  echo "Venv already exists: $VENV_NAME"
fi

# shellcheck disable=SC1090
source "$VENV_NAME/bin/activate"

python -m pip install --upgrade pip

if [[ -z "$EXTRAS" || "$EXTRAS" == "none" ]]; then
  echo "Installing editable (no extras)..."
  pip install -e .
else
  if [[ "$EXTRAS" =~ ^\[.*\]$ ]]; then
    EXTRAS_SPEC=".$EXTRAS"
  else
    EXTRAS_SPEC=".[${EXTRAS}]"
  fi
  echo "Installing editable with extras: $EXTRAS_SPEC"
  pip install --upgrade -e "$EXTRAS_SPEC"
fi

if [[ "$INSTALL_KERNEL" == "1" ]]; then
  echo "Installing ipykernel + registering kernel..."
  pip install ipykernel
  KERNEL_NAME="$(basename "$(pwd)" | tr ' ' '-' )"
  python -m ipykernel install --user --name "$KERNEL_NAME" --display-name "Python ($KERNEL_NAME)"
  echo "Kernel registered as: Python ($KERNEL_NAME)"
fi

echo
echo "Done."
echo "Activate later with:"
echo "  source $VENV_NAME/bin/activate"
