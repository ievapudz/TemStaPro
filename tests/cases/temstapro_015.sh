#!/bin/sh

# Testing case with replaced symbols of the sequence

./thermoclass2  -f tests/data/replaced_symbol_sequence.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --per-res-output ./tests/outputs/015_mean.tmp 

rm ./tests/outputs/015_mean.tmp

