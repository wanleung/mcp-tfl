#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEARCH_DIR="$(dirname "${SCRIPT_DIR}")"
SELF_PATH="$(realpath "$0")"

while [ "${SEARCH_DIR}" != "/" ]; do
    TARGET_PATH="${SEARCH_DIR}/scripts/deploy_test.sh"
    if [ -f "${TARGET_PATH}" ] \
        && [ -f "${SEARCH_DIR}/README.md" ] \
        && [ -f "${SEARCH_DIR}/main.py" ] \
        && [ "$(realpath "${TARGET_PATH}")" != "${SELF_PATH}" ]; then
        exec bash "${TARGET_PATH}"
    fi
    SEARCH_DIR="$(dirname "${SEARCH_DIR}")"
done

echo "Unable to locate repository root with scripts/deploy_test.sh" >&2
exit 1
