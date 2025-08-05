#!/usr/bin/env python3
"""
Parallel FASTQ K-mer Randomizer for HPC clusters
Randomizes reads by shuffling non-overlapping k-mers for k=1 to 35
Optimized for processing 50+ million reads using multiprocessing
"""

import random
import sys
import os
from multiprocessing import Pool, cpu_count
from functools import partial
import gzip

def randomize_kmers(sequence, quality, k):
    """Shuffle non-overlapping k-mers in a sequence"""
    if len(sequence) < k:
        return sequence, quality
    
    # Get non-overlapping k-mers
    seq_kmers = [sequence[i:i+k] for i in range(0, len(sequence), k)]
    qual_kmers = [quality[i:i+k] for i in range(0, len(quality), k)]
    
    # Shuffle them together
    paired = list(zip(seq_kmers, qual_kmers))
    random.shuffle(paired)
    
    # Reconstruct
    shuffled_seq, shuffled_qual = zip(*paired)
    return ''.join(shuffled_seq), ''.join(shuffled_qual)

def process_reads_for_k(args):
    """Process all reads for a specific k-mer size"""
    k, input_file, output_base, chunk_size = args
    
    output_file = f"{output_base}_k{k}.fastq"
    print(f"Processing k={k}...")
    
    opener = gzip.open if input_file.endswith('.gz') else open
    mode = 'rt' if input_file.endswith('.gz') else 'r'
    
    reads_processed = 0
    
    with opener(input_file, mode) as infile, open(output_file, 'w') as outfile:
        while True:
            # Read one record at a time
            header = infile.readline().strip()
            if not header:
                break
                
            sequence = infile.readline().strip()
            plus = infile.readline().strip()
            quality = infile.readline().strip()
            
            # Process this read
            rand_seq, rand_qual = randomize_kmers(sequence, quality, k)
            
            # Write result
            outfile.write(f"{header}\n{rand_seq}\n{plus}\n{rand_qual}\n")
            
            reads_processed += 1
            if reads_processed % 1000000 == 0:
                print(f"  k={k}: Processed {reads_processed:,} reads")
    
    print(f"Completed k={k} - Total reads: {reads_processed:,}")
    return k, reads_processed

def process_chunk_for_all_k(args):
    """Process a chunk of reads for all k values (alternative approach)"""
    chunk_data, k_values, output_base, chunk_id = args
    
    # Dictionary to store results for each k
    results = {k: [] for k in k_values}
    
    # Process each read in the chunk for all k values
    for header, sequence, plus, quality in chunk_data:
        for k in k_values:
            rand_seq, rand_qual = randomize_kmers(sequence, quality, k)
            results[k].append((header, rand_seq, plus, rand_qual))
    
    # Write results to temporary files
    temp_files = {}
    for k in k_values:
        temp_file = f"{output_base}_k{k}_chunk{chunk_id}.tmp"
        temp_files[k] = temp_file
        
        with open(temp_file, 'w') as f:
            for header, sequence, plus, quality in results[k]:
                f.write(f"{header}\n{sequence}\n{plus}\n{quality}\n")
    
    return temp_files

def read_fastq_chunks(filename, chunk_size=50000):
    """Generator that yields chunks of FASTQ reads"""
    opener = gzip.open if filename.endswith('.gz') else open
    mode = 'rt' if filename.endswith('.gz') else 'r'
    
    chunk = []
    with opener(filename, mode) as f:
        while True:
            header = f.readline().strip()
            if not header:
                if chunk:
                    yield chunk
                break
            
            sequence = f.readline().strip()
            plus = f.readline().strip()
            quality = f.readline().strip()
            
            chunk.append((header, sequence, plus, quality))
            
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []

def merge_temp_files(output_base, k_values, num_chunks):
    """Merge temporary chunk files into final outputs"""
    for k in k_values:
        output_file = f"{output_base}_k{k}.fastq"
        with open(output_file, 'w') as outfile:
            for chunk_id in range(num_chunks):
                temp_file = f"{output_base}_k{k}_chunk{chunk_id}.tmp"
                if os.path.exists(temp_file):
                    with open(temp_file, 'r') as infile:
                        outfile.write(infile.read())
                    os.remove(temp_file)
        print(f"Merged k={k}")

def process_by_k_parallel(input_file, output_base, max_processes):
    """Process by parallelizing across k values (simpler, no nested pools)"""
    k_values = list(range(1, 36))
    chunk_size = 100000  # Not used in this approach, but kept for consistency
    
    # Create arguments for each k value
    args_list = [(k, input_file, output_base, chunk_size) for k in k_values]
    
    print(f"Processing k=1 to 35 in parallel using {max_processes} processes")
    
    with Pool(processes=max_processes) as pool:
        results = pool.map(process_reads_for_k, args_list)
    
    return results

def process_by_chunks_parallel(input_file, output_base, chunk_size, max_processes):
    """Process by parallelizing across chunks (more memory efficient for huge files)"""
    k_values = list(range(1, 36))
    
    print(f"Processing in chunks of {chunk_size:,} reads using {max_processes} processes")
    
    # Process chunks in parallel
    chunk_args = []
    chunk_id = 0
    
    for chunk in read_fastq_chunks(input_file, chunk_size):
        chunk_args.append((chunk, k_values, output_base, chunk_id))
        chunk_id += 1
        
        # Process in batches to avoid memory issues
        if len(chunk_args) >= max_processes:
            with Pool(processes=max_processes) as pool:
                pool.map(process_chunk_for_all_k, chunk_args)
            chunk_args = []
    
    # Process remaining chunks
    if chunk_args:
        with Pool(processes=max_processes) as pool:
            pool.map(process_chunk_for_all_k, chunk_args)
    
    # Merge temporary files
    print("Merging temporary files...")
    merge_temp_files(output_base, k_values, chunk_id)

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 6:
        print("Usage: python script.py input.fastq output_base [max_processes] [method] [chunk_size]")
        print("  input.fastq     - Input FASTQ file (can be .gz)")
        print("  output_base     - Output base name")
        print("  max_processes   - Max parallel processes (default: min(35, CPU_count))")
        print("  method          - 'k' (parallel by k-mer) or 'chunk' (parallel by chunks)")
        print("  chunk_size      - Reads per chunk for 'chunk' method (default: 50000)")
        print()
        print("Method 'k': Faster for smaller files, one process per k-mer size")
        print("Method 'chunk': More memory efficient for huge files (50M+ reads)")
        print()
        print("Creates: output_base_k1.fastq, output_base_k2.fastq, ..., output_base_k35.fastq")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_base = sys.argv[2]
    max_processes = int(sys.argv[3]) if len(sys.argv) > 3 else min(35, cpu_count())
    method = sys.argv[4] if len(sys.argv) > 4 else 'k'
    chunk_size = int(sys.argv[5]) if len(sys.argv) > 5 else 50000
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    print(f"Input file: {input_file}")
    print(f"Output base: {output_base}")
    print(f"Available CPUs: {cpu_count()}")
    print(f"Using {max_processes} processes")
    print(f"Processing method: {method}")
    
    if method == 'k':
        # Parallel processing by k-mer size (simpler, faster for moderate files)
        process_by_k_parallel(input_file, output_base, max_processes)
    elif method == 'chunk':
        # Parallel processing by chunks (more memory efficient)
        process_by_chunks_parallel(input_file, output_base, chunk_size, max_processes)
    else:
        print("Error: Method must be 'k' or 'chunk'")
        sys.exit(1)
    
    print(f"\nDone! Created 35 files with k-mer sizes 1-35")
    print(f"Output files: {output_base}_k1.fastq to {output_base}_k35.fastq")

if __name__ == "__main__":
    main()