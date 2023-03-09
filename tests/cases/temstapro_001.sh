#!/bin/sh

# Testing case with replaced symbols of the sequence

./temstapro  -f tests/data/replaced_symbol_sequence.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --per-res-output ./tests/outputs/001_mean.tmp 

rm -f ./tests/outputs/001_mean.tmp

