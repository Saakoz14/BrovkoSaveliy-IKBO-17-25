#!/bin/bash
text="$*"
line=$(printf '%*s' $((${#text}+2)) | tr ' ' '-')
echo "+$line+"
echo "| $text |"
echo "+$line+"
