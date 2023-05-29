"""
Representing the output of the program.
"""

import numpy
import matplotlib.pyplot as plt

def get_temperature_label(predictions, temperature_ranges, left_hand=True):
    """
    Process the raw output of the inference model to get temperature range 
    labels.

    predictions - LIST that contains predictions for each temperature range
    temperature_ranges - LIST with temperature ranges' labels
    left_hand - BOOLEAN that indicates to find the left-hand 
        (True) or right-hand (False) limit

    returns STRING that is the label of the limiting temperature range
    """
    if(left_hand):
        for j, pred in enumerate(predictions):
            if(float(pred) < 0.5):
                return temperature_ranges[j]
            elif(float(pred) >= 0.5 and j != len(predictions)-1):
                continue
            else:
                return temperature_ranges[-1]
    else:
        for j, pred in enumerate(predictions[::-1]):
            if(float(pred) >= 0.5):
                return temperature_ranges[len(predictions)-j]
            elif(float(pred) < 0.5 and j != len(predictions)-1):
                continue
            else:
                return temperature_ranges[0]

def detect_clash(predictions, left_hand=True):
    """
    Detecting the conflicting predictions of the ensemble.

    predictions - LIST that contains predictions for each temperature range
    left_hand - BOOLEAN that indicates to find the clash from left-hand 
        (True) or right-hand (False)
    
    returns STRING '-' if clash was not detected, '*' if it was
    """	
    if(left_hand):
        for j, pred in enumerate(predictions):
            if(j and round(float(predictions[j-1])) <
                round(float(predictions[j]))):
                return "*"
            elif(j and round(float(predictions[j-1])) >=
                round(float(predictions[j])) and j != len(predictions)-1):
                continue
            elif(j and round(float(predictions[j-1])) >=
                round(float(predictions[j])) and j == len(predictions)-1):
                return "-"
    else:
        for j, pred in enumerate(predictions[::-1]):
            if(j != len(predictions)-1 and round(float(predictions[j-1])) <
                round(float(predictions[j]))):
                return "yes"
            elif(j != len(predictions)-1 and round(float(predictions[j-1])) >=
                round(float(predictions[j])) and j != len(predictions)-2):
                continue
            elif(j != len(predictions)-1 and round(float(predictions[j-1])) >=
                round(float(predictions[j])) and j == len(predictions)-2):
                return "no"

def print_inferences_header(file_handle, input_fasta=False):
    """
    Print inferences table header.

    file_handle - FILE to which the results will be printed
    input_fasta - BOOLEAN that determines whether the input was FASTA (True)
        or NPZ (False)
    """

    if(input_fasta):
        print("protein_id\tposition\tsequence\tlength\t"+\
            "t40_binary\tt40_raw\tt45_binary\tt45_raw\tt50_binary\tt50_raw\t"+\
            "t55_binary\tt55_raw\tt60_binary\tt60_raw\tt65_binary\tt65_raw\t"+\
            "t70_binary\tt70_raw\tt75_binary\tt75_raw\tt80_binary\tt80_raw\t"+\
            "left_hand_label\tright_hand_label\tclash", file=file_handle)
    else:
        print("protein_id\tposition\t"+\
            "t40_binary\tt40_raw\tt45_binary\tt45_raw\tt50_binary\tt50_raw\t"+\
            "t55_binary\tt55_raw\tt60_binary\tt60_raw\tt65_binary\tt65_raw\t"+\
            "t70_binary\tt70_raw\tt75_binary\tt75_raw\tt80_binary\tt80_raw\t"+\
            "left_hand_label\tright_hand_label\tclash", file=file_handle)

def print_inferences(averaged_inferences, binary_inferences, original_headers,
    labels, clashes, file_handle, sequences=None, input_fasta=False, 
    run_mode='mean'):
    """
    Print results.

    averaged_inferences - LIST of DICT that keeps each sequence's mean inferences
    binary_inferences - LIST of DICT that keeps each sequence's binary inferences
    original_headers - DICT of original sequences' headers for printing
    labels - LIST of DICT that keeps each sequence's left-hand and right-hand 
        temperature prediction labels
    clashes - LIST of DICT that keeps each sequence's clash labels
    sequences - LIST of DICT that keeps sequence ids as keys and sequences as values
    file_handle - FILE to which the results will be printed
    input_fasta - BOOLEAN that determines whether the input was FASTA (True)
        or NPZ (False)
    run_mode - STRING that determines which run mode is executed:
        'mean', 'per-res', 'per-segment'
    """

    if(sequences is None): return

    for proc_header in averaged_inferences.keys():
        merged_inferences = []
        for i, inf in enumerate(binary_inferences[proc_header]):
            merged_inferences.append("%d" % binary_inferences[proc_header][i])
            merged_inferences.append("%.3e" % averaged_inferences[proc_header][i])

        # Setting the default values for run_mode 'mean'
        if(run_mode == "mean"):
            out_header = original_headers[proc_header]
            position = '-'
        elif(run_mode == "per-segment"):
            out_header = original_headers["_".join(proc_header.split("_")[0:-1])]
            pos_range = proc_header.split("_")[-1].split("-")
            range_length = int(pos_range[1])-int(pos_range[0])
            # Calculating the position (numerated from 1)
            position = str(int(pos_range[0])+int(range_length/2)+1)
        elif(run_mode == "per-res"):
            out_header = original_headers["_".join(proc_header.split("_")[0:-1])]
            position = str(int(proc_header.split("_")[-1])+1)

        if(input_fasta):
            print("%s\t%s\t%s\t%d\t%s\t%s\t%s" % (out_header, position, 
                sequences[proc_header],
                len(sequences[proc_header]), "\t".join(merged_inferences),
                "\t".join(labels[proc_header]), clashes[proc_header][0]), file=file_handle)
        else:
            print("%s\t%s\t%s\t%s\t%s" % (out_header, position, "\t".join(merged_inferences),
                "\t".join(labels[proc_header]), clashes[proc_header][0]), file=file_handle)


def plot_per_res_inferences(averaged_inferences, thresholds, plot_dir, 
    smoothen=True, window_size=21, x_label="residue index", 
    title="Per-residue predictions"):
    """
    Plotting per-residue inferences.

    averaged_inferences - DICT that keeps each sequence's inferences 
        (averaged of all threshold models))
    thresholds - LIST with binary models' temperature thresholds
    plot_dir - STRING that determines the directory where plots should 
        be saved
    smoothen - BOOL indicates to plot smoothened curve
    """
    WINDOW_SIZE = window_size

    original_seq_ids = set()
    for seq_id in averaged_inferences.keys():
        original_seq_ids.add("_".join(seq_id.split("_")[0:-1]))
    original_seq_ids = list(original_seq_ids)
  
    offset = 0 
    for or_seq_id in sorted(original_seq_ids):
        x_values = []
        y_values = []

        # Python3.7+: DICT has the keys sorted by the insertion order
        for i, seq_id in enumerate(list(averaged_inferences.keys())):
            if(or_seq_id == "_".join(seq_id.split("_")[0:-1])):
                x_values.append(i-offset)
                y_values.append(averaged_inferences[seq_id])

        y_values = numpy.array(y_values).T
        
        for i, threshold in enumerate(thresholds):
            plt.figure(f"t{threshold} models' per-residue inferences for {seq_id}")
            color = "lightgrey" if(smoothen) else "navy"
            plt.plot(x_values, y_values[i], linewidth=1, color=color)
            plt.xlabel(x_label)
            plt.ylabel("prediction")
            plt.title(f"{title} of {or_seq_id} using threshold {threshold}", wrap=True)
            plt.ylim(bottom=0, top=1)
            j = 0
            y_smoothened_values = []
  
            if(smoothen):
                while j < len(y_values[i])-WINDOW_SIZE+1:
                    window_average = round(numpy.sum(
                        y_values[i][j:j+WINDOW_SIZE])/WINDOW_SIZE, 2)
          
                    y_smoothened_values.append(window_average)
                    j += 1
      
                plt.plot(x_values[int(WINDOW_SIZE/2):-int(WINDOW_SIZE/2)], 
                    y_smoothened_values, linewidth=1, color="navy")
            
            plt.savefig(f"{plot_dir}/{or_seq_id}_per_residue_plot_t{threshold}.svg", format="svg")

        offset += len(x_values)

def plot_inferences(per_res_out, per_segment_out, averaged_inferences, thresholds, plot_dir,
    window_size, segment_size, smoothen):
    """
    Deciding and calling, which inferences to plot.

    per_res_out - STRING or None to determine whether per-residue predictions 
        are required
    per_segment_out - STRING or None to determine whether per-segment 
        predictions are required
    averaged_inferences - DICT that keeps each sequence's inferences 
        (averaged of all threshold models))
    thresholds - LIST with binary models' temperature thresholds
    plot_dir - STRING that determines the directory where plots should 
        be saved
    window_size - INT of the window size for curve smoothening
    segment_size - INT of the segment size of combined residues
    smoothen - BOOL indicates to plot smoothened curve
    """
    if(plot_dir is None): return 
    if(per_res_out):
        plot_per_res_inferences(averaged_inferences, thresholds,
            plot_dir, window_size=window_size)

    if(per_segment_out):
        plot_per_res_inferences(averaged_inferences, thresholds,
            plot_dir, smoothen=smoothen,
            window_size=window_size,
            x_label=f"segment (k={segment_size}) index",
        title="Per-segment predictions")
