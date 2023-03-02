#!/bin/sh

# Testing downloading of the ProtTrans model

if test -f "./ProtTrans/config.json"; then
    rm ./ProtTrans/config.json
fi

if test -f "./ProtTrans/pytorch_model.bin"; then
    rm ./ProtTrans/pytorch_model.bin
fi

./thermoclass2 -f ./tests/data/long_sequence.fasta \
    -e tests/outputs -d './ProtTrans/'/

rm tests/outputs/b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt
