#!/bin/sh

# Testing passing FASTA sequence as '-f' option and embeddings generation with 
# cache

./temstapro -f ./tests/data/long_sequence_2.fasta -e 'tests/outputs/' -d './ProtTrans/' \
    --mean-out tests/outputs/002.tmp

rm -f tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt

rm -f tests/outputs/002.tmp
