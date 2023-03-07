#!/bin/sh

# Testing making per-residue inferences and plotting

if test -f "tests/outputs/mean_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt"; then
    rm tests/outputs/mean_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt
fi

if test -f "tests/outputs/per_res_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt"; then
    rm tests/outputs/per_res_519c2e9a42194ade71c697d64ed3bced3175a6324803a940ebdf69bb65f301ec.pt
fi

if test -f "tests/outputs/mean_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt"; then
    rm tests/outputs/mean_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt
fi

if test -f "tests/outputs/per_res_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt"; then
    rm tests/outputs/per_res_7bdb2d9587a23bb7f744bcffba509cc7adf8c69667a9d954c3be1a4aa09f7c0a.pt
fi

if test -f "tests/outputs/mean_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt"; then
    rm tests/outputs/mean_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt
fi

if test -f "tests/outputs/per_res_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt"; then
    rm tests/outputs/per_res_d2a3c93ce60d9c7ed923bda5def8fa46267df336f7310cc3e951a20f092df979.pt
fi

./temstapro -f tests/data/multiple_short_sequences.fasta \
    -e './tests/outputs/' -d './ProtTrans/' \
    -p './tests/outputs/' --mean-output ./tests/outputs/010_mean.tmp \
    --per-res-output ./tests/outputs/010_per_res.tmp

rm ./tests/outputs/short_seq_?_per_residue_plot_?.svg 
rm ./tests/outputs/010_mean.tmp ./tests/outputs/010_per_res.tmp
