#!/usr/bin/env python3
"""
Take a counts file and a proportion (default 0.99 for 99%)
Report NA for any value that makes up less than that proportion of the sample count
Then drop any taxa that are NA in all samples.
"""

import sys
import os
import pandas as pd
import numpy as np

def get_decimal_places(value):
    """Get the number of decimal places in a number"""
    str_val = str(value)
    if '.' in str_val:
        return len(str_val.split('.')[1])
    return 0

def main():
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Need to supply a count table with samples as rows and taxa as columns.", file=sys.stderr)
        sys.exit(1)
    
    table_file = sys.argv[1]
    prop = 0.99
    output_file = None
    
    if len(sys.argv) > 2:
        prop = float(sys.argv[2])
        print(f"User specified proportion: {prop}")
    else:
        print(f"Using default proportion: {prop}")
    
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
        print(f"User specified output file: {output_file}")
    
    print(f"Only reporting taxa that account for at least {prop * 100}% of the counts for a given sample.")
    
    # Read the count table
    print(f"Reading count table from: {table_file}")
    try:
        counts = pd.read_csv(table_file, sep='\t', index_col=0)
    except FileNotFoundError:
        print(f"Error: File '{table_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if the table was read correctly
    if counts.shape[0] == 0:
        print("Count table is empty or could not be read properly.", file=sys.stderr)
        sys.exit(1)
    if counts.shape[1] == 0:
        print("Count table has no taxa columns.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loaded table with {counts.shape[0]} samples and {counts.shape[1]} taxa.")
    
    # Calculate row sums (total counts per sample)
    row_sums = counts.sum(axis=1)
    
    # Check for samples with zero counts
    zero_count_samples = (row_sums == 0).sum()
    if zero_count_samples > 0:
        print(f"Warning: Found {zero_count_samples} samples with zero total counts.")
        print("These samples will have all taxa set to NA.")
    
    # Calculate number of decimal places in prop for rounding
    prop_decimal_places = get_decimal_places(prop)
    
    # Apply proportion filter
    # For each sample (row), set taxa to NA if they don't meet the proportion threshold
    # and convert remaining values to proportions (0-1)
    filtered_counts = counts.copy()
    
    for i in range(len(counts)):
        if row_sums.iloc[i] > 0:
            # Calculate proportions for this sample
            sample_props = counts.iloc[i] / row_sums.iloc[i]
            # Round proportions to match prop decimal places
            sample_props_rounded = sample_props.round(prop_decimal_places)
            # Set values to NA if they don't meet the threshold, otherwise use rounded proportion
            mask = sample_props < prop
            filtered_counts.iloc[i] = sample_props_rounded
            filtered_counts.iloc[i][mask] = np.nan
        else:
            # If sample has zero total counts, set all to NA
            filtered_counts.iloc[i] = np.nan
    
    # Count how many values were set to NA
    total_values = counts.shape[0] * counts.shape[1]
    na_values = filtered_counts.isna().sum().sum()
    print(f"Set {na_values} out of {total_values} values to NA ({na_values/total_values * 100:.2f}%).")
    
    # Remove taxa that are NA in all samples
    taxa_all_na = filtered_counts.isna().all(axis=0)
    filtered_counts = filtered_counts.loc[:, ~taxa_all_na]
    
    n_removed_taxa = taxa_all_na.sum()
    print(f"Removed {n_removed_taxa} taxa that were NA in all samples.")
    print(f"Final table has {filtered_counts.shape[0]} samples and {filtered_counts.shape[1]} taxa.")
    
    # Generate output filename
    if output_file is None:
        # Extract base name and extension
        base_name = os.path.splitext(os.path.basename(table_file))[0]
        extension = os.path.splitext(os.path.basename(table_file))[1]
        
        if extension == "":
            output_file = f"{base_name}_minProportion-{prop}"
        else:
            output_file = f"{base_name}_minProportion-{prop}{extension}"
    
    # Write the filtered table
    filtered_counts.to_csv(output_file, sep='\t', na_rep='NA')
    
    print(f"Filtered proportion table written to: {output_file}")

if __name__ == "__main__":
    main()
