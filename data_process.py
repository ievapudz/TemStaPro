"""
Process the data set before the inference process.
"""

import numpy
import torch
from hashlib import sha256
from os import path

def get_sequences_without_embeddings(sequences, emb_dir, per_res=False):
    """
    Collecting sequences that do not have generated embeddings.

    sequences - DICT of all sequences in the input (keys are sequence ids, 
        values are protein sequences
    emb_dir - STRING that defines the directory where embeddings are saved
    per_res - BOOL that determines whether per-residue embeddings are needed

    returns DICT with sequences that lack embeddings
    """
    seqs_wo_emb = {}
    for seq_id in list(sequences.keys()):
        seq_code = sha256(sequences[seq_id].encode('utf-8')).hexdigest()
        if(not path.exists(f"{emb_dir}/mean_{seq_code}.pt")):
            seqs_wo_emb[seq_id] = sequences[seq_id]
        if(per_res and not path.exists(f"{emb_dir}/per_res_{seq_code}.pt")):
            seqs_wo_emb[seq_id] = sequences[seq_id]
    return seqs_wo_emb

def collect_mean_embeddings(sequences, embeddings, emb_dir, input_size=1024):
    """
    Collecting mean embeddings into a dictionary.

    sequences - DICT of all sequences in the input (keys are sequence ids,
        values are protein sequences
    embeddings - DICT with generated embeddings. Keys are "mean_representations"
        and "per_res_representations", which have [DICT] values, which keys are 
        sequence ids and values are embeddings torch tensor
    emb_dir - STRING that determines the path to the embeddings 'cache' 
        directory
    input_size - INT that notes the dimension of each embeddings vector

    returns DICT with keys "x_test" (values are embeddings tensors) and 
        "y_test" (values are (irrelevant) temperature labels)
    """
    dataset = {}
    dataset['y_test'] = torch.tensor((), dtype=torch.int32)
    for i, seq_id in enumerate(sequences):
        if(emb_dir and path.exists(emb_dir)):
            # Loading sequences from cache
            embedding = torch.load("%s/mean_%s.pt" % (emb_dir,
                sha256(sequences[seq_id].encode('utf-8')).hexdigest()))["mean_representations"]
        else:
            # Taking freshly-generated embeddings
            embedding = torch.from_numpy(embeddings["mean_representations"][seq_id])
        if(i):
            dataset["x_test"] = torch.vstack((dataset["x_test"], torch.flatten(embedding)))
        else:
            dataset["x_test"] = torch.reshape(embedding, (1, input_size))
        dataset["y_test"] = torch.cat((dataset["y_test"], torch.tensor([999]).int()), 0)
    return dataset

def collect_per_res_embeddings(sequences, original_sequences, embeddings, emb_dir, 
    input_size=1024, smoothen=False, window_size=21):
    """
    Collecting per-residue embeddings into a dictionary.

    sequences - DICT of all sequences in the input (keys are sequence ids,
        values are protein sequences
    embeddings - DICT with generated embeddings. Keys are "mean_representations"
        and "per_res_representations", which have [DICT] values, which keys are 
        sequence ids and values are embeddings torch tensor
    emb_dir - STRING that determines the path to the embeddings 'cache' 
        directory
    input_size - INT that notes the dimension of each embeddings vector
    smoothen - BOOL indicates whether to make average smoothing of embeddings

    returns DICT with keys "x_test" (values are embeddings tensors) and 
        "y_test" (values are fake temperature labels)
    """
    dataset = {}
    dataset['y_test'] = torch.tensor((), dtype=torch.int32)
    dataset['z_test'] = {}

    for i, seq_id in enumerate(sequences):

        iterations_for_seq = len(sequences[seq_id])

        if(emb_dir and path.exists(emb_dir)):
            embedding = torch.load("%s/per_res_%s.pt" % (emb_dir,
                sha256(sequences[seq_id].encode('utf-8')).hexdigest()))["per_res_representations"]
        else:
            # Taking freshly-generated embeddings
            embedding = torch.from_numpy(embeddings["per_res_representations"][seq_id])

        for j in range(iterations_for_seq):
            if(i == 0 and j == 0):
                dataset["x_test"] = torch.reshape(embedding[j], (1, input_size))
            else:
                dataset["x_test"] = torch.vstack((dataset["x_test"], torch.flatten(embedding[j])))
            if(not smoothen): dataset["y_test"] = torch.cat((dataset["y_test"], torch.tensor([999]).int()), 0)
            if(not smoothen): dataset["z_test"]['%s_%d' % (seq_id, j)] = original_sequences[seq_id][j]

        if(smoothen):
            WINDOW_SIZE = window_size
            smoothened_seqs = {}
            j = 0
            while(j < iterations_for_seq-WINDOW_SIZE+1):
                smoothened_embedding = dataset["x_test"][range(j, j+WINDOW_SIZE)].mean(dim=0)
                if(not j and not i):
                    smoothened_embeddings = smoothened_embedding
                else:
                    smoothened_embeddings = torch.vstack((smoothened_embeddings, smoothened_embedding))
                dataset['z_test']['%s_%d-%d' % (seq_id, j, j+WINDOW_SIZE)] = ''.join(original_sequences[seq_id][j:j+WINDOW_SIZE])
                dataset["y_test"] = torch.cat((dataset["y_test"], torch.tensor([999]).int()), 0)
                j += 1
    
    if(smoothen): dataset["x_test"] = smoothened_embeddings
    return dataset

def load_tensor_from_NPZ(NPZ_file, keywords):
    """
    Loading embeddings from file to dictionary.

    NPZ_file - STRING path to the NPZ file
    keywords - LIST with keywords to identify which subset of file to load
    
    returns DICT with keys as given keywords, values in tensors
    """
    dataset = {}
    with numpy.load(NPZ_file, allow_pickle=True) as data_loaded:
    	for i in range(len(keywords)):
            dataset[keywords[i]] = torch.from_numpy(data_loaded[keywords[i]])
    return dataset
