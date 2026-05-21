# TemStaPro - classification of proteins based on thermostability

## Hardware requirements

Any modern CPU can be used for calculations. Although, have 
in mind that average laptop CPU (e.g. Intel i7-8565U), 
will take ~60 times longer (~10 hours) to predict thermostability of 1000 sequences (average length of 
1137 residues, using `--portion-size 0`), 
compared to a GPU 
version of a program (~10 minutes)
running on a system with NVIDIA GeForce RTX 2080 Ti 
and Intel i9-9900K CPU.

Other hardware systems, which were used to successfully run the program:

- CPU: Intel Xeon Silver 4110 (2,10 GHz)
- GPU: NVIDIA A100 80GB PCIe

## Environment requirements

TemStaPro now ships with a `pyproject.toml` and supports modern Python
versions. Python 3.12 is the recommended version for new environments.
Any supported version matching the package metadata (`>=3.9`) should work.

Create a Python environment first, then install TemStaPro from the local
checkout with `pip`.

For a GPU-enabled environment:
```
python3.12 -m venv temstapro_env
source temstapro_env/bin/activate
python -m pip install --upgrade pip
pip install "torch==2.6.0"
pip install .
```

For a CPU-only environment, install the CPU build of PyTorch first and then
install TemStaPro:
```
python3.12 -m venv temstapro_env
source temstapro_env/bin/activate
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install .
```

To verify that PyTorch can see CUDA when expected:
```
python -c "import torch; print(torch.cuda.is_available())"
```

## Downloading the program

To download the program, go to the directory of your choice in your system.
If you have `git` installed, run the following command:

```
git clone https://github.com/NeurosnapInc/TemStaPro.git
cd TemStaPro
```

If there is no `git` in your system, press on the (green) button 'Code'
and then 'Download ZIP'. The ZIP archyve containing the program's code will be
shortly downloaded. Next step is to decompress the archyve in the directory of 
your choice.

## Testing the set-up

Test if the environment was installed and the program was downloaded 
successfully:
```
pip install -e ".[test]"
pytest -q
```

The CLI golden tests may download ProtTrans assets on first use. If that
causes a mismatch in expected output, rerun the tests after the initial
download completes.

To run a single CLI golden test case:
```
pytest -q tests/test_cli.py -k 004
```

## Usage

To get a list of all possible options run:
```
./temstapro --help
```

ProtTrans weights are downloaded on demand into `./ProtTrans/` the first time
they are needed.

If you prefer not to run TemStaPro locally, Neurosnap provides a hosted
webserver for running TemStaPro interactively and in bulk:
https://neurosnap.ai/service/TemStaPro%20Protein%20Thermostability%20Prediction

The main workflow of the program is to take FASTA files of protein
sequences and provide predictions for them from mean ProtTrans embeddings. 

Since embeddings generation is the bottleneck process regarding 
the performance of the tool, it is recommended to use '-e' option 
to make cache embeddings files in case there is a need to run the 
program more than once.

```
./temstapro -f ./tests/data/long_sequence.fasta -d ./ProtTrans/ \
    -e tests/outputs/ --mean-output ./long_sequence_predictions.tsv
```

It is possible to retrieve predictions for each amino acid in the protein 
by using the output choice '--per-res-output'. This mode provides plot for per-residue
predictions if the option '-p' is given.

```
./temstapro -f tests/data/long_sequence.fasta -e './tests/outputs/' \
    -d ./ProtTrans/ -p './' \
    --per-res-output ./long_sequence_predictions_per_res.tsv
```

The mode 'per-segment' makes predictions for a window (size k=41) of 
amino acids. If '-p' option is given, a plot is generated. This mode also has 
'--curve-smoothening' option to additionally smoothen the curve of the plot.

```
./temstapro -f tests/data/long_sequence.fasta -e './tests/outputs/' \
    -d ./ProtTrans/ --curve-smoothening -p './' \
    --per-segment-output ./long_sequence_predictions_k41.tsv
```

## Running program with SLURM

```
srun ./temstapro -f tests/data/long_sequence.fasta \
    -d ./ProtTrans/ -t './' --mean-output tests/outputs/long_sequence.tsv
```

## Interpretation of the results

The default output of the program is a TSV table with binary and raw predictions
from the ensemble of binary classifiers for temperature thresholds: 
40, 45, 50, 55, 60, 65. The table also contains a predicted temperature labels
retrieved by the interpretation of the raw predictions of each threshold. 
The value in column 'clash' indicates, whether there was an inconsistency ("\*") in 
classifiers' predictions or not ('-').

If plotting option is chosen, five plots (for each classifiers' predictions) 
will be created. The naming convention is 
'[FASTA header of protein]\_per\_residue\_plot\_t[40|45|50|55|60|65|70|75|80].svg'

## Dataset availability

Datasets that were used to train, validate, and test TemStaPro are available in 
[Zenodo.](https://doi.org/10.5281/zenodo.7743637)

## Citing

If you use TemStaPro in your publication, please cite the [work.](https://doi.org/10.1093/bioinformatics/btae157)

```

@article{pudziuvelyte_temstapro_2024,
	title = {{TemStaPro}: protein thermostability prediction using sequence representations from protein language models},
	volume = {40},
	issn = {1367-4811},
	shorttitle = {{TemStaPro}},
	url = {https://doi.org/10.1093/bioinformatics/btae157},
	doi = {10.1093/bioinformatics/btae157},
	abstract = {Reliable prediction of protein thermostability from its sequence is valuable for both academic and industrial research. This prediction problem can be tackled using machine learning and by taking advantage of the recent blossoming of deep learning methods for sequence analysis. These methods can facilitate training on more data and, possibly, enable the development of more versatile thermostability predictors for multiple ranges of temperatures.We applied the principle of transfer learning to predict protein thermostability using embeddings generated by protein language models (pLMs) from an input protein sequence. We used large pLMs that were pre-trained on hundreds of millions of known sequences. The embeddings from such models allowed us to efficiently train and validate a high-performing prediction method using over one million sequences that we collected from organisms with annotated growth temperatures. Our method, TemStaPro (Temperatures of Stability for Proteins), was used to predict thermostability of CRISPR-Cas Class II effector proteins (C2EPs). Predictions indicated sharp differences among groups of C2EPs in terms of thermostability and were largely in tune with previously published and our newly obtained experimental data.TemStaPro software and the related data are freely available from https://github.com/ievapudz/TemStaPro and https://doi.org/10.5281/zenodo.7743637.},
	number = {4},
	urldate = {2024-04-09},
	journal = {Bioinformatics},
	author = {Pud{\v z}iuvelyt{\. e}, Ieva and Olechnovi{\v c}, Kliment and Godliauskaite, Egle and Sermokas, Kristupas and Urbaitis, Tomas and Gasiunas, Giedrius and Kazlauskas, Darius},
	month = apr,
	year = {2024},
	pages = {btae157},
}

```
