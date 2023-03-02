"""
Workflow regarding the inference making process.
"""

from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import numpy

def prepare_data_loaders(datasets, keyword):
    """
    Preparing and returning DataLoader objects.

    datasets - LIST of dictionaries that hold data sets
    keyword - STRING the suffix of keywords of the dictionary
    run_mode - STRING that determines the running mode of the program
    
    returns (DataLoader, DataLoader)
    """
    test_dataset = TensorDataset(datasets[0]['x_'+keyword],
        datasets[0]['y_'+keyword])
    test_loader = DataLoader(test_dataset, shuffle=False)

    per_res_test_loader = None
    if(datasets[1]):
        per_res_test_dataset = TensorDataset(datasets[1]['x_'+keyword],
            datasets[1]['y_'+keyword])
        per_res_test_loader = DataLoader(per_res_test_dataset, shuffle=False) 
    
    return (test_loader, per_res_test_loader)

def prepare_inference_dictionaries(sequences_list, is_npz=False):
    """
    Initialising dictionaries to save inferences.

    sequences_lists - LIST of dictionaries with information about sequences
    is_npz - BOOLEAN that indicates whether an NPZ file or a FASTA file is 
        processed

    returns (LIST, LIST, LIST, LIST)
    """
    averaged_inferences = []
    binary_inferences = []
    labels = []
    clashes = [] 

    if(is_npz):
        averaged_inferences.append({})
        binary_inferences.append({})
        labels.append({})
        clashes.append({})
        for seq in sequences_list[0]:
            averaged_inferences[0][seq[0].split("|")[1]] = []
            binary_inferences[0][seq[0].split("|")[1]] = []
            labels[0][seq[0].split("|")[1]] = []
            clashes[0][seq[0].split("|")[1]] = []
    else:
        for i, seq_dict in enumerate(sequences_list):
            if(seq_dict is None): break
            averaged_inferences.append({})
            binary_inferences.append({})
            labels.append({})
            clashes.append({})
            for seq in seq_dict.keys():
                averaged_inferences[i][seq] = []
                binary_inferences[i][seq] = []
                labels[i][seq] = []
                clashes[i][seq] = []
    
    return (averaged_inferences, binary_inferences, labels, clashes)

def inference_epoch(model, test_loader, identifiers=[], device="cpu"):
    """
    Making inferences for each given protein sequence.

    model - torch.nn.Module with a defined architecture
    test_loader - DataLoader with a dataset loaded for inferences
    identifiers - LIST with sequence identifiers used as keys in inferences DICT
    device - STRING that determines the processor used

    returns DICT with inferences 
    """
    inferences = {}
    for i, data in enumerate(test_loader, 0):
        inputs, targets = data
        inputs, targets = inputs.to(device), targets.to(device)
        outputs = model(inputs.float())
        outputs = outputs.detach().cpu().numpy()
        
        seq_id = identifiers[i]
        
        for output in outputs: 
            inferences[seq_id] = output[1]

    return inferences
