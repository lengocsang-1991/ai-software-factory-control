#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3 -m factory_control init
printf 'Dashboard: http://127.0.0.1:8765/\n'
exec python3 -m factory_control serve
