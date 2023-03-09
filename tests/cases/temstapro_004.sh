#!/bin/sh

# Testing downloading of the ProtTrans model

rm -f ./ProtTrans/config.json
rm -f ./ProtTrans/pytorch_model.bin

./temstapro -f ./tests/data/long_sequence_2.fasta \
    -e 'tests/outputs' -d './ProtTrans/' --mean-out tests/outputs/004.tmp

rm -f tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt
rm -f tests/outputs/004.tmp
