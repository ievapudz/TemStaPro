#!/bin/sh

# Testing making per-residue inferences

rm -f tests/outputs/5d817ae8188e00eca8913c80312e2669d6551777fbed0d1764e1c09386638c0a.pt
rm -f tests/outputs/adc7fcd839ba2802998088a0c7b2310d3abdef0229cc020c55fcb82a492c2d8d.pt
rm -f tests/outputs/c425721d82cb786570760210076eaa21403b210aa6566882a41c4ac70df2defd.pt

./temstapro -f tests/data/multiple_sequences.fasta -e './tests/outputs/' \
    -d './ProtTrans/' --mean-output tests/outputs/012_mean.tmp \
    --per-res-output tests/outputs/012_per_res.tmp

rm -f ./tests/outputs/012_mean.tmp 
rm -f ./tests/outputs/012_per_res.tmp
