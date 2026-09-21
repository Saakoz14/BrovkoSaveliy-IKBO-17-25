#!/bin/bash
tar -cf archive.tar -- *."${1#.}"
