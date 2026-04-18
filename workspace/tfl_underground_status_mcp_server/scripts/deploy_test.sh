#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEARCH_DIR="${SCRIPT_DIR}"

while [ "${SEARCH_DIR}" != "/" ]; do
    if [ -f "${SEARCH_DIR}/scripts/deploy_test.sh" ]; then
        exec bash "${SEARCH_DIR}/scripts/deploy_test.sh"
    fi
    SEARCH_DIR="$(dirname "${SEARCH_DIR}")"
done

echo "Unable to locate repository root with scripts/deploy_test.sh" >&2
exit 1
