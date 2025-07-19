#!/usr/bin/env python3
"""
Genome chopping script that takes a FASTA file and produces overlapping chunks in FASTQ format.
"""

import argparse
import os
import random
import gzip
from pathlib import Path


def read_fasta(filepath):
    """Read FASTA file and return sequence name and sequence."""
    sequences = {}
    current_name = None
    current_seq = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_name:
                    sequences[current_name] = ''.join(current_seq)
                current_name = line[1:]  # Remove '>' character
                current_seq = []
            else:
                current_seq.append(line)
        
        # Don't forget the last sequence
        if current_name:
            sequences[current_name] = ''.join(current_seq)
    
    return sequences


def chop_sequence(sequence, chunk_size, slide_bp, max_sequences=None):
    """Generate overlapping chunks from a sequence."""
    chunks = []
    seq_len = len(sequence)
    
    if slide_bp == 0:
        # Random sequence mode
        if max_sequences is None:
            max_sequences = 100  # Default for random mode
        
        # Generate random start positions
        valid_starts = list(range(seq_len - chunk_size + 1))
        if len(valid_starts) == 0:
            return chunks  # Sequence too short
        
        # Sample random starts (with replacement if needed)
        num_chunks = min(max_sequences, len(valid_starts))
        random_starts = random.sample(valid_starts, min(num_chunks, len(valid_starts)))
        
        # If we need more sequences than unique positions, sample with replacement
        if max_sequences > len(valid_starts):
            additional_needed = max_sequences - len(valid_starts)
            random_starts.extend(random.choices(valid_starts, k=additional_needed))
        
        # Sort starts for consistent output
        random_starts.sort()
        
        for start in random_starts:
            end = start + chunk_size
            chunk = sequence[start:end]
            chunks.append((start, end - 1, chunk))
            
    else:
        # Regular sliding window mode
        for start in range(0, seq_len - chunk_size + 1, slide_bp):
            end = start + chunk_size
            chunk = sequence[start:end]
            chunks.append((start, end - 1, chunk))
            
            # Check if we've reached max sequences
            if max_sequences and len(chunks) >= max_sequences:
                break
                
            # Break if we've reached the end
            if end >= seq_len:
                break
    
    return chunks


def write_fastq(output_file, chunks, input_filename, seq_name, use_gzip=False):
    """Write chunks to FASTQ format with Illumina-style headers."""
    base_filename = Path(input_filename).stem  # Get filename without extension
    
    # Choose file opening method based on gzip option
    open_func = gzip.open if use_gzip else open
    mode = 'wt' if use_gzip else 'w'
    
    with open_func(output_file, mode) as f:
        for i, (start, end, chunk) in enumerate(chunks):
            # Illumina-style FASTQ format:
            # @instrument:run:flowcell:lane:tile:x:y read:filtered:control:index
            # sequence
            # +optional_description
            # quality_scores
            
            # Create Illumina-style header
            instrument = "SIM"  # Simulator
            run = "001"
            flowcell = "INSILICO"
            lane = "1"
            tile = str(i + 1).zfill(4)  # Tile number based on sequence index
            x_coord = str(start).zfill(5)  # X coordinate as start position
            y_coord = str(end).zfill(5)    # Y coordinate as end position
            read_num = "1"  # Single-end read
            filtered = "N"  # Not filtered
            control = "0"   # Not a control
            index = "ATCG"  # Simple index
            
            seq_id = f"{instrument}:{run}:{flowcell}:{lane}:{tile}:{x_coord}:{y_coord} {read_num}:{filtered}:{control}:{index}"
            quality = "I" * len(chunk)  # High quality scores (Illumina Q40)
            
            f.write(f"@{seq_id}\n")
            f.write(f"{chunk}\n")
            f.write(f"+{base_filename}:{start}-{end}\n")  # Keep genomic coordinates in comment line
            f.write(f"{quality}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Chop genome sequences into overlapping chunks",
        epilog="""
Examples:
  %(prog)s -i input.fa -c 100 -s 50                       # 100bp chunks, 50bp steps
  %(prog)s -i input.fa -c 75 -s 25 -n 1000               # Limit to 1000 sequences
  %(prog)s -i input.fa -c 150 -s 0 -n 500                # Random mode: 500 random 150bp chunks
  %(prog)s -i input.fa -c 200 -s 100 -o results/         # Output to directory with default name
  %(prog)s -i input.fa -c 100 -s 50 -z                   # Gzip compressed output
  %(prog)s -i input.fa -c 100 -s 50 -o output/ -z        # Gzip output to directory
  %(prog)s --input-file genome.fa --chunk-size 200 --slide-bp 100  # Long form options

Output Options:
  -o filename.fastq    : Specific output filename
  -o directory/        : Use default filename in specified directory
  -z                   : Compress output with gzip (.gz extension added automatically)

Modes:
  Sliding window mode (slide-bp > 0): Creates overlapping chunks at regular intervals
  Random mode (slide-bp = 0): Selects random start positions for chunks

The script reads FASTA format files and outputs overlapping sequence chunks
in FASTQ format with Illumina-style headers and high-quality base scores. 
Each output sequence uses standard Illumina header format for compatibility
with downstream tools like Kraken, BWA, etc.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-i", "--input-file", required=True, help="Input FASTA file path")
    parser.add_argument("-c", "--chunk-size", type=int, required=True, help="Size of each chunk (in bases)")
    parser.add_argument("-s", "--slide-bp", type=int, required=True, help="Step size between chunks (in bases). Use 0 for random mode")
    parser.add_argument("-n", "--max-sequences", type=int, help="Maximum number of output sequences to produce")
    parser.add_argument("-o", "--output", help="Output FASTQ file or directory. If directory (ends with /), uses default filename. Default: input_name_chopped.fastq in input directory")
    parser.add_argument("-z", "--gzip", action="store_true", help="Compress output with gzip (.gz extension added automatically)")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    
    args = parser.parse_args()
    
    # Read input FASTA
    sequences = read_fasta(args.input_file)
    
    # Determine output filename
    if args.output:
        output_path = Path(args.output)
        # Check if output is a directory (ends with / or is an existing directory)
        if str(args.output).endswith('/') or (output_path.exists() and output_path.is_dir()):
            # Use directory with default filename
            input_path = Path(args.input_file)
            default_filename = f"{input_path.stem}_chopped.fastq"
            if args.gzip:
                default_filename += ".gz"
            output_file = output_path / default_filename
        else:
            # Use as specified filename
            output_file = output_path
            # Add .gz extension if gzip requested and not already present
            if args.gzip and not str(output_file).endswith('.gz'):
                output_file = Path(str(output_file) + '.gz')
    else:
        # Generate default filename in same directory as input
        input_path = Path(args.input_file)
        default_filename = f"{input_path.stem}_chopped.fastq"
        if args.gzip:
            default_filename += ".gz"
        output_file = input_path.parent / default_filename
    
    # Process each sequence in the FASTA file
    all_chunks = []
    total_input_bases = 0
    
    for seq_name, sequence in sequences.items():
        total_input_bases += len(sequence)
        chunks = chop_sequence(sequence, args.chunk_size, args.slide_bp, args.max_sequences)
        all_chunks.extend(chunks)
        
        mode_info = "random" if args.slide_bp == 0 else "sliding window"
        print(f"Processed sequence '{seq_name}' ({mode_info} mode): {len(sequence)} bases -> {len(chunks)} chunks")
        
        # If we have max_sequences limit and we've reached it, break
        if args.max_sequences and len(all_chunks) >= args.max_sequences:
            all_chunks = all_chunks[:args.max_sequences]  # Trim to exact limit
            break
    
    # Calculate coverage statistics
    total_output_bases = len(all_chunks) * args.chunk_size
    average_coverage = total_output_bases / total_input_bases if total_input_bases > 0 else 0
    
    # Write all chunks to output file
    # Use the first sequence name for the output (assuming single sequence for now)
    first_seq_name = list(sequences.keys())[0]
    write_fastq(output_file, all_chunks, args.input_file, first_seq_name, args.gzip)
    
    print(f"Output written to: {output_file}")
    print(f"Total chunks generated: {len(all_chunks)}")
    print(f"Total input bases: {total_input_bases:,}")
    print(f"Total output bases: {total_output_bases:,}")
    print(f"Average coverage: {average_coverage:.2f}x")


if __name__ == "__main__":
    main()
