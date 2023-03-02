#!/bin/sh

# Testing passing FASTA sequence as '-f' option and embeddings generation with 
# cache

./thermoclass2 -f ./tests/data/long_sequence.fasta -e tests/outputs/ \
    -d './ProtTrans/'
