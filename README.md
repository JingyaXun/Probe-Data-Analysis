# Probe Data Analysis

Run task 1 and 2:

```
python map_matching.py path_to_probe_data_dir/ path_to__dir/
```


Run task 3:

```
python single_smear_detection.py path_to_img_dir/ path_to_output_dir/
```

# Assignment #2
### Probe Data Analysis for Road Slope
### Boyu Wang, Jingya Xun

## Requirements
Python 3.6
```
pip install pandas
pip install numpy
pip install csv
```

## Running the Script

Our project handles three tasks
1. Map match probe points to road links.
2. Derive road slope for each road link.
3. Evaluate the derived road slope with the surveyed road slope in the link data file.


### Run task 1 and 2
Make sure your data files are in the same directory with script. To run the script, simply input the following commands in Terminal:

```
python3 map_matching.py map_match
```
#### Output Files

1. `Partition6467MatchedPoints.csv`

### Run task 3
Make sure your data files are in the same directory with script. To run the script, simply input the following commands in Terminal:

```
python3 map_matching.py slope_eval
```
#### Output Files

1. `eval.csv`

