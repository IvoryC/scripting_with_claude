#!/bin/bash

# Get input file from argument or use default
INPUT_FILE=${1:-input/test_input_full-alphabet.fastq}

echo "Using input file: $INPUT_FILE"

mkdir temp

# Loop through iterations 1 through 5
for i in {1..5}; do
    echo "Processing iteration $i..."
    
    # Run shuffle script
    python resource/shuffle_claude.py $INPUT_FILE temp/shuffled_${i}.fastq
    
    # Run verification script  
    python artifacts/fastq_verify.py $INPUT_FILE temp/shuffled_${i}.fastq_k1.fastq -o output/
    
    echo "Completed iteration $i"
done

echo "All iterations completed."
