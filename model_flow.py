"""
Workflow regarding the inference making process.
"""

from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import numpy
from MLP import MLP_C2H2
import torch

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

def make_inferences(sequences, per_res_sequences, mean_loader, per_res_loader, 
	parameters, thresholds_range): 
	"""
	Making inferences.
   
	sequences - DICT with the sequences' ids as keys and amino acid sequences as values
	per_res_sequences - DICT with the sequences' ids as keys and amino acid sequences as values 
	mean_loader - DataLoader to load mean embeddings data
	per_res_loader - DataLoader to load per-reside embeddings data
	hidden_layer_sizes - LIST with sizes (INT) of the hidden layers of classifiers
	parameters - DICT with values of keys: THRESHOLDS, SEEDS, HIDDEN_LAYER_SIZES, CLASSIFIERS_DIR, EMB_TYPE, DATASET, CLASSIFIER_TYPE
	thresholds_range - STRING to determine, which thresholds to choose

	returns (DICT, DICT, DICT, DICT)
	"""
	averaged_inferences, binary_inferences, labels, clashes = prepare_inference_dictionaries(
		[sequences, per_res_sequences])

	for j, loader in enumerate([mean_loader, per_res_loader]):
		if(loader is None): break
		for threshold in parameters["THRESHOLDS"][thresholds_range]:
			threshold_inferences = {}
			for seed in parameters["SEEDS"]:
				classifier = MLP_C2H2(parameters["INPUT_SIZE"], 
					parameters["HIDDEN_LAYER_SIZES"][0],
					parameters["HIDDEN_LAYER_SIZES"][1])
				model_path = "%s/%s_%s_%s-%s_s%s.pt" % (
					parameters["CLASSIFIERS_DIR"], parameters["EMB_TYPE"], 
					parameters["DATASET"], parameters["CLASSIFIER_TYPE"], 
					threshold, seed)
	
				classifier.load_state_dict(torch.load(model_path, map_location=torch.device(parameters['DEVICE'])))
				classifier.eval()

				classifier.to(parameters["DEVICE"])

				threshold_inferences[seed] = inference_epoch(classifier,
					loader,
					identifiers=list(averaged_inferences[j].keys()), device=parameters["DEVICE"])
			# Taking average of the predictions 
			for seq in threshold_inferences["41"].keys():
				mean_prediction = 0
				for seed in parameters["SEEDS"]:
					 mean_prediction += threshold_inferences[seed][seq]
				mean_prediction /= len(parameters["SEEDS"])
				averaged_inferences[j][seq].append(mean_prediction)
				binary_inferences[j][seq].append(round(mean_prediction))
	return (averaged_inferences, binary_inferences, labels, clashes)
