#!/bin/sh

# Testing writing to the given output

./thermoclass2 -n ./tests/data/long_sequence.npz -d './ProtTrans/' \
    --mean-output ./tests/outputs/006.tmp

rm ./tests/outputs/006.tmp
