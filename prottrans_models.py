"""
A module that works with ProtTrans models. Functions were
adapted from ProtTrans authors' Google Colab notebook
"""

from transformers import T5EncoderModel, T5Tokenizer
import torch
import os
import sys
from hashlib import sha256

def get_pretrained_model(model_path):
    """
    Fetches the model accordingly to the model_path
    model_path - STRING that identifies the model to fetch
    Returns model.
    """

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    if(os.path.exists(model_path+'/pytorch_model.bin') and 
        os.path.exists(model_path+'/config.json')):
        model = T5EncoderModel.from_pretrained(model_path+'/pytorch_model.bin', 
                    config=model_path+'/config.json')
    else:
        model = T5EncoderModel.from_pretrained(model_path)
    model = model.to(device)
    model = model.eval()

    return model

def save_pretrained_model(model, path_to_dir):
    """
    Saves the model to the file (PT).
    model - OBJ [PreTrainedModel] of the model to save
    path_to_dir - STRING that identifies the destination to save the model
    """

    model.save_pretrained(path_to_dir)

def get_tokenizer(model_path):
    """
    Fetches the tokenizer accordingly to the model_path
    model_path - STRING that identifies the model whose tokenizer 
				 should be fetched
    Returns tokenizer.
    """
    if(os.path.exists(model_path+'/pytorch_model.bin') and 
        os.path.exists(model_path+'/config.json')):
        tokenizer = T5Tokenizer.from_pretrained(model_path+'/pytorch_model.bin',
	    config=model_path+'/config.json', do_lower_case=False)
    else:
        tokenizer = T5Tokenizer.from_pretrained(model_path, do_lower_case=False)
	
    return tokenizer

def load_model_and_tokenizer(pt_dir, pt_server_path):
    """
    Load ProtTrans model and tokenizer.
    
    pt_dir - STRING to determine the path to the directory with ProtTrans 
        "pytorch_model.bin" file
    pt_server_path - STRING of the path to ProtTrans model in its server
    """
    if(os.path.isfile(f"{pt_dir}/pytorch_model.bin")):
        model = get_pretrained_model(pt_dir)
    else:
        if(not os.path.exists(f"{pt_dir}/")):
            os.system(f"mkdir -p {pt_dir}/")
        model = get_pretrained_model(pt_server_path)
        save_pretrained_model(model, pt_dir)

    tokenizer = get_tokenizer(pt_server_path)

    return (model, tokenizer)

def process_FASTA(fasta_path, split_char="!", id_field=0):
    """
    Reads in fasta file containing multiple sequences.
    Split_char and id_field allow to control identifier extraction from header.
    E.g.: set split_char="|" and id_field=1 for SwissProt/UniProt Headers.
    Returns dictionary holding multiple sequences or only single 
    sequence, depending on input file.
    """
	
    seqs = dict()
    orig_seq_headers = dict()
    orig_seqs = dict()
    with open(fasta_path, 'r') as fasta_f:
        for line in fasta_f:
            if line.startswith('>'):
                uniprot_id = line.replace('>', '').strip().split(split_char)[id_field]
                uniprot_id = uniprot_id.replace("/", "_").replace(".", "_")
                seqs[uniprot_id] = ''
                orig_seq_headers[uniprot_id] = line.replace('>', '').strip()
                orig_seqs[uniprot_id] = ''
            else:
                orig_seqs[uniprot_id] += line.strip()
                seq = ''.join(line.split()).upper().replace("-", "")
                seq = seq.replace('U','X').replace('Z', 'X').replace('O', 'X')
                seqs[uniprot_id] += seq 
    example_id = next(iter(seqs))

    return (seqs, orig_seq_headers, orig_seqs)

def get_embeddings(model, tokenizer, seqs, per_residue, per_protein, 
                    max_residues=4000, # number of cumulative residues per batch
                    max_seq_len=2000, # max length after which we switch to single-sequence processing to avoid OOM
                    max_batch=100 # max number of sequences per single batch
    ):
    """
    Generation of embeddings via batch-processing.
    per_residue indicates that embeddings for each residue in a protein
        should be returned.
    per_protein indicates that embeddings for a whole protein should be
        returned (average-pooling).
    Returns results depending on the option in the input.
    """

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    results = {'per_res_representations': dict(),
		'mean_representations': dict()}
    seq_dict = sorted(seqs.items(), key=lambda kv: len(seqs[kv[0]]), 
        reverse=True)
    batch = list()

    for seq_idx, (pdb_id, seq) in enumerate(seq_dict, 1):
        seq_len = len(seq)
        seq = ' '.join(list(seq))
        batch.append((pdb_id, seq, seq_len))

        n_res_batch = sum([s_len for _, _, s_len in batch]) + seq_len

        if (len(batch) >= max_batch) or (n_res_batch >= max_residues) or (seq_idx == len(seq_dict)) or (seq_len > max_seq_len):
            pdb_ids, seqs, seq_lens = zip(*batch)
            batch = list()

            token_encoding = tokenizer.batch_encode_plus(seqs, 
                add_special_tokens=True, padding='longest')
            input_ids = torch.tensor(token_encoding['input_ids']).to(device)
            attention_mask = torch.tensor(
                token_encoding['attention_mask']).to(device)
            
            try:
                with torch.no_grad():
                    embedding_repr = model(input_ids, 
                        attention_mask=attention_mask)
            except RuntimeError:
                print(f"{sys.argv[0]}: runtime error generating embedding for {pdb_id} (L={seq_len}). "+\
                    f"Try lowering batch size. If single sequence processing does not work, you need "+\
                    f"more vRAM to process your protein.", file=sys.stderr)
                continue

            for batch_idx, identifier in enumerate(pdb_ids):
                s_len = seq_lens[batch_idx]
                emb = embedding_repr.last_hidden_state[batch_idx,:s_len]
                if per_residue:
                    results["per_res_representations"][identifier] = \
                        emb.detach().cpu().numpy().squeeze()
                if per_protein:
                    protein_emb = emb.mean(dim=0)
                    results["mean_representations"][identifier] = \
                        protein_emb.detach().cpu().numpy().squeeze()

    return results

def save_embeddings(sequences, embeddings, embeddings_directory, embedding_type="mean"):
    """
    Saving embeddings to PT files for later use.

    sequences - DICT with sequence ids as keys and sequences themselves 
    as values
    embeddings - DICT with generated embeddings for each sequence
    embeddings_directory - STRING that determines the path to directory for embeddings
    embedding_type - STRING that determines, which type of embeddings to save
    """
    embedding_type_key = embedding_type+"_representations"
    for seq_id in list(sequences.keys()):
        seq_data = {"label": seq_id}
        if(seq_id in embeddings[embedding_type_key].keys()):
            seq_data["sequence"] = sequences[seq_id]
            seq_data[embedding_type_key] = torch.from_numpy(
                embeddings[embedding_type_key][seq_id])
        seq_code = sha256(sequences[seq_id].encode('utf-8')).hexdigest()
        torch.save(seq_data, f"{embeddings_directory}/{embedding_type}_{seq_code}.pt")

def print_embeddings_generation_stats(iteration, portion_size, embeddings, 
    seqs_wo_emb, start_time, end_time):
    """
    Printing embeddings generation statistics.

    iteration - INT index of the iteration (indexing from zero)
    portion_size - INT size of the processed portion
    embeddings - DICT with keys 'mean_representations' and 'per_res_representations'
    seqs_wo_emb - DICT with a portion of sequence ids as keys and amino acid sequences as values
    start_time - time of the beginning of embeddings' generation
    end_time - time of the end of embeddings' generation
    """
    print(f"Portion {int(iteration/portion_size)+1}.", file=sys.stderr)
    print(f"{len(embeddings['mean_representations'].keys())}/{len(list(seqs_wo_emb.keys()))}: "+\
        "sequences with generated mean embeddings",
        file=sys.stderr)
    print(f"{len(embeddings['per_res_representations'].keys())}/{len(list(seqs_wo_emb.keys()))}: "+\
        "sequences with generated per-residue embeddings",
        file=sys.stderr)
    print("%s: time to generate embeddings" % (end_time - start_time),
        file=sys.stderr)
    print("%s: time to generate embeddings per protein" % ((end_time - \
        start_time)/len(embeddings["mean_representations"])),
        file=sys.stderr)
