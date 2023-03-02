#!/bin/sh

# Testing case with a very long sequence (expected error)

./temstapro  -f tests/data/extra_long_sequence.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --mean-output ./tests/outputs/014_mean.tmp \

