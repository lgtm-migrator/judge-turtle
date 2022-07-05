#!/bin/bash

ROOT="$(dirname "$(dirname "$0")")"

cd "$ROOT" || exit

pytest \
    --pylama \
    --ignore="tests" \
    "$@"
