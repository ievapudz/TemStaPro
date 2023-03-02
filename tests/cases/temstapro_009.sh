#!/bin/sh

# Testing passing FASTA sequence as '-f' option and embeddings generation with no cache used

./thermoclass2 -f ./tests/data/long_sequence.fasta -d './ProtTrans/'

