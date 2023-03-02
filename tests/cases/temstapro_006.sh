#!/bin/sh

# Testing writing to the given output

./temstapro -n ./tests/data/long_sequence.npz -d './ProtTrans/' \
    --mean-output ./tests/outputs/006.tmp

rm ./tests/outputs/006.tmp
