#!/bin/sh

# Testing making per-residue inferences

rm -f tests/outputs/mean_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt
rm -f tests/outputs/per_res_b6f8b4d2f6602ee040278b1d64ab7cf588baa33d74a126030e252fd91ac00601.pt

./temstapro  -f tests/data/long_sequence.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --mean-output ./tests/outputs/006_mean.tmp \
    --per-segment-output ./tests/outputs/006_per_res_smooth.tmp \
    -c --segment-size 41 --window-size-predictions 81 -p './tests/outputs/'

rm -f ./tests/outputs/006_mean.tmp
rm -f ./tests/outputs/006_per_res_smooth.tmp
