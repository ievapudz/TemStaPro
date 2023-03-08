#!/bin/sh

# Testing downloading of the ProtTrans model

if test -f "./ProtTrans/config.json"; then
    rm ./ProtTrans/config.json
fi

if test -f "./ProtTrans/pytorch_model.bin"; then
    rm ./ProtTrans/pytorch_model.bin
fi

./temstapro -f ./tests/data/long_sequence_2.fasta \
    -e 'tests/outputs' -d './ProtTrans/' --mean-out tests/outputs/004.tmp

rm tests/outputs/mean_52ae55d4fc194abf0e65abc9d740ffc7f84972ddacefb62e931131655083857e.pt
rm tests/outputs/004.tmp
