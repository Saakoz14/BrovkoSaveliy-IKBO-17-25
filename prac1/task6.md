#!/bin/bash
find "${1:-.}" -type f \( -name '*.c' -o -name '*.js' -o -name '*.py' \) |
while read -r file; do
    case $file in
        *.py) pattern='^[[:space:]]*#' ;;
        *) pattern='^[[:space:]]*(//|/\*)' ;;
    esac
    if head -n 1 "$file" | grep -Eq "$pattern"; then
        echo "$file: комментарий есть"
    else
        echo "$file: комментария нет"
    fi
done
