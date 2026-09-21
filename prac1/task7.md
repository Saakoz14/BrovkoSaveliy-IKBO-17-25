#!/bin/bash
find "$1" -type f -exec sha256sum {} + | sort | uniq -w 64 -D
