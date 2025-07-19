#!/usr/bin/env python3
"""
Sort tab-delimited file by adding a count column, sorting rows hierarchically,
and sorting taxa columns by frequency.
"""

import sys
import os
import pandas as pd

def sort_tsv_file(input_file):
    """
    Sort a tab-delimited file by adding a count column and sorting rows.
    
    Args:
        input_file (str): Path to input tab-delimited file
    """
    try:
        # Read the tab-delimited file
        df = pd.read_csv(input_file, sep='\t', index_col=0)
        
        # Sort taxa (columns) by frequency - most represented taxa first
        taxa_counts = df.apply(lambda col: ((col != 0) & col.notna()).sum(), axis=0)
        sorted_taxa = taxa_counts.sort_values(ascending=False).index
        df = df[sorted_taxa]
        
        # Count non-zero/non-null values in each row (excluding NA values)
        count_col = df.apply(lambda row: ((row != 0) & row.notna()).sum(), axis=1)
        
        # Insert count column as the first column
        df.insert(0, 'count', count_col)
        
        # Sort by all columns in order (count first, then original columns)
        df_sorted = df.sort_values(by=list(df.columns), ascending=True)
        
        # Generate output filename
        base_name = os.path.splitext(input_file)[0]
        extension = os.path.splitext(input_file)[1]
        output_file = f"{base_name}_sorted{extension}"
        
        # Write sorted data to output file
        df_sorted.to_csv(output_file, sep='\t')
        
        print(f"Sorted file saved as: {output_file}")
        print(f"Added count column and sorted {len(df_sorted)} rows")
        print(f"Sorted {len(sorted_taxa)} taxa by frequency (most common first)")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python sort_tsv.py <input_file>")
        print("Example: python sort_tsv.py data.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)
    
    sort_tsv_file(input_file)

if __name__ == "__main__":
    main()
