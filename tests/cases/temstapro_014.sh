#!/bin/sh

# Testing passing FASTA sequence as '-f' option and getting predictions of t20
# classifier

./temstapro -f ./tests/data/long_sequence_2.fasta -e 'tests/outputs/' -d './ProtTrans/' \
    --mean-out tests/outputs/014.tmp --thresholds-range ':(20]:'

rm -f tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt

rm -f tests/outputs/014.tmp
