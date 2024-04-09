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

Before starting up Anaconda or Miniconda should be installed
in the system. Follow instructions given in 
[Conda's documentation.](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

Setting up the environment can be done in one of the following ways.

### From YML file

In this repository two YML files can be found: one YML file
has the prerequisites for the environment that exploits only 
CPU ([`environment_CPU.yml`](./environment_CPU.yml)), another one to exploit both CPU 
GPU ([`environment_GPU.yml`](./environment_GPU.yml)).

This approach was tested with Conda 4.10.3 and 4.12.0 versions.

Run the following command to create the environment from a 
YML file:
```
conda env create -f environment_CPU.yml
```

Activate the environment:
```
conda activate temstapro_env_CPU
```

### From scratch

To set up the environment to exploit GPU for the program, run the following commands:
```
conda create -n temstapro_env python=3.7
conda activate temstapro_env
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
conda install -c conda-forge transformers
conda install -c conda-forge sentencepiece
conda install -c conda-forge matplotlib
```

To test if PyTorch package is installed to exploit CUDA,
call `python3` command interpreter and run the 
following lines:
```
import torch
torch.cuda.is_available()
```

If the output is 'True', then the installing procedure was successful,
otherwise try to set the path to the installed packages:
```
export PATH=/usr/local/cuda-11.7/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64\${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

If CUDA for PyTorch is still not available, check out the [forum.](https://github.com/pytorch/pytorch/issues/30664)

For the systems without GPU, run the following commands:
```
conda create -n temstapro_env python=3.7
conda activate temstapro_env
conda install -c conda-forge transformers
conda install pytorch -c pytorch
conda install -c conda-forge sentencepiece
conda install -c conda-forge matplotlib
```

## Downloading the program

To download the program, go to the directory of your choice in your system.
If you have `git` installed, run the following command:

```
git clone https://github.com/ievapudz/TemStaPro.git
```

If there is no `git` in your system, press on the (green) button 'Code'
and then 'Download ZIP'. The ZIP archyve containing the program's code will be
shortly downloaded. Next step is to decompress the archyve in the directory of 
your choice.

## Testing the set-up

Test if the environment was installed and the program was downloaded 
successfully:
```
make all
```

It might be that the tests will not pass on the first
try because of "Downloading" messages. If this is 
the case, clean the output files
and run the tests again using commands:

```
make clean
make all
```

## Usage

To get a list of all possible options run:
```
./temstapro --help
```

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
	file = {Full Text PDF:/Users/ievapudz/Zotero/storage/8SBYAFBZ/Pud{\v z}iuvelyt{\. e} et al. - 2024 - TemStaPro protein thermostability prediction usin.pdf:application/pdf;Snapshot:/Users/ievapudz/Zotero/storage/WK73JHM7/7632735.html:text/html},
}

```
