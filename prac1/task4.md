#!/bin/bash
grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | paste -sd ' ' -
