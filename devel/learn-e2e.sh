#!/bin/bash

ROOT="$(dirname "$(dirname "$0")")"

cd "$ROOT" || exit

git submodule update --init

LEARN_OUTPUT="YES" pytest tests/test_e2e.py -v -s
