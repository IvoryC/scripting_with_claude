#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gzip
import random
import shutil

from concurrent.futures import ProcessPoolExecutor, as_completed

def shuffle_sequence(sequence,n):
    kmers = [sequence[i:i+n] for i in range(0, len(sequence) - len(sequence) % n, n)]
    # Extract remainder
    remainder = sequence[len(sequence) - len(sequence) % n:]
    kmers.append(remainder)
    # Shuffle the 2-mers
    random.shuffle(kmers)
    # Reassemble sequence from shuffled 2-mers and remainder
    randomized_sequence = ''.join(kmers)
    return randomized_sequence

def process_chunk(chunk,n):
    output = []
    for i in range(0, len(chunk), 4):
        header = chunk[i]
        sequence = chunk[i+1]
        plus_line = chunk[i+2]
        quality = chunk[i+3]

        randomized_sequence= shuffle_sequence(sequence.strip(),n)
        output.extend([header, randomized_sequence + '\n', f'+ shuffled {n}-mers\n', quality])
    return output

def randomize_fastq_sequences(input_file, output_file,mer_l, chunk_size=1000000):
    num_cpus = int(os.getenv('SLURM_CPUS_ON_NODE', os.cpu_count()))
    print(num_cpus)
    with open_fastq_file(input_file) as infile, open(output_file, 'w') as outfile:
        with ProcessPoolExecutor(max_workers=num_cpus) as executor:
            futures = []
            chunk = []

            for line in infile:
                chunk.append(line)
                if len(chunk) >= chunk_size * 4:
                    futures.append(executor.submit(process_chunk, chunk,mer_l))
                    chunk = []

            if chunk:
                futures.append(executor.submit(process_chunk, chunk,mer_l))

            for future in as_completed(futures):
                outfile.writelines(future.result())


def open_fastq_file(filename):
    """Open FASTQ file, handling both regular and gzipped files."""
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')  # 'rt' for read text mode
    else:
        return open(filename, 'r')

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file> [output_directory] [nmer]")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist")
        sys.exit(1)

    # Check if input file is a FASTQ file (including gzipped)
    valid_extensions = ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
    if not any(input_file.lower().endswith(ext) for ext in valid_extensions):
        print("Error: Input file must be a FASTQ file (.fastq, .fq, .fastq.gz, or .fq.gz extension)")
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()

    # Handle nmer argument with error checking
    if len(sys.argv) > 3:
        try:
            nmer = int(sys.argv[3])
        except ValueError:
            print("Error: nmer must be an integer")
            sys.exit(1)
    else:
        nmer = 1

    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create output filename
    input_filename = os.path.basename(input_file)
    base_name, extension = os.path.splitext(input_filename)

    output_filename = f"{base_name}_shuffle_{nmer}mer{extension}"
    output_file = os.path.join(output_dir, output_filename)

    # Call the randomization function
    randomize_fastq_sequences(input_file, output_file, mer_l=nmer)

    # Gzip the output file
    gzipped_output = output_file + '.gz'
    with open(output_file, 'rb') as f_in:
        with gzip.open(gzipped_output, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Remove the uncompressed file
    os.remove(output_file)

    print(f"Output written to: {gzipped_output}")

if __name__ == "__main__":
    main()