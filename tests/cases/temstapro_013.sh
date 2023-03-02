#!/bin/sh

# Testing making per-residue inferences

if test -f "tests/outputs/b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt"; then
    rm tests/outputs/b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt
fi

./temstapro  -f tests/data/long_sequence.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --mean-output ./tests/outputs/013_mean.tmp \
    --per-segment-output ./tests/outputs/013_per_res_smooth.tmp \
    -c --segment-size 41 --window-size-predictions 81 -p './tests/outputs/'

rm ./tests/outputs/013_mean.tmp
rm ./tests/outputs/013_per_res_smooth.tmp
