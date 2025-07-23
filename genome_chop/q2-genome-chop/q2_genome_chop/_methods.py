import os
import gzip
import random
import tempfile
from pathlib import Path
from typing import Optional

import pandas as pd
from q2_types.feature_data import DNAFASTAFormat
from q2_types.per_sample_sequences import SingleLanePerSampleSingleEndFastqDirFmt


def chop_sequences(
    sequences: DNAFASTAFormat,
    chunk_size: int,
    slide_bp: int,
    max_sequences: Optional[int] = None,
    random_seed: Optional[int] = None,
    sample_name: Optional[str] = None
) -> SingleLanePerSampleSingleEndFastqDirFmt:
    """
    Chop genome sequences into overlapping chunks.
    
    Parameters
    ----------
    sequences : DNAFASTAFormat
        Input DNA sequences in FASTA format
    chunk_size : int
        Size of each sequence chunk in base pairs
    slide_bp : int
        Step size between chunks in base pairs. Use 0 for random mode
    max_sequences : int, optional
        Maximum number of output sequences to produce
    random_seed : int, optional
        Random seed for reproducible random mode
    sample_name : str, optional
        Custom sample name for output. If not provided, generates descriptive 
        name based on parameters (e.g., 'sliding_chunks_c100_s50' or 'random_chunks_c150_n500')
        
    Returns
    -------
    SingleLanePerSampleSingleEndFastqDirFmt
        Chopped sequences in FASTQ format (always gzip compressed)
    """
    
    # Set random seed if provided
    if random_seed is not None:
        random.seed(random_seed)
    
    # Create output directory format
    result = SingleLanePerSampleSingleEndFastqDirFmt()
    
    # Read sequences from the FASTA format object
    sequences_dict = _read_fasta(str(sequences))
    
    # Generate sample ID - use custom name if provided, otherwise create descriptive name
    if sample_name:
        sample_id = sample_name
    else:
        # Generate descriptive name based on parameters
        if slide_bp == 0:
            # Random mode
            max_str = str(max_sequences) if max_sequences else 'all'
            sample_id = f"random_chunks_c{chunk_size}_n{max_str}"
        else:
            # Sliding window mode
            sample_id = f"sliding_chunks_c{chunk_size}_s{slide_bp}"
    
    # Process all sequences in this file
    all_chunks = []
    total_input_bases = 0
    
    for seq_name, sequence in sequences_dict.items():
        total_input_bases += len(sequence)
        chunks = _chop_sequence(sequence, chunk_size, slide_bp, max_sequences)
        
        # Add metadata to chunks
        for i, (start, end, chunk_seq) in enumerate(chunks):
            chunk_id = f"{sample_id}_{seq_name}_{start}_{end}"
            all_chunks.append((chunk_id, start, end, chunk_seq))
        
        # If we have max_sequences limit and we've reached it, break
        if max_sequences and len(all_chunks) >= max_sequences:
            all_chunks = all_chunks[:max_sequences]
            break
    
    # Write FASTQ output - QIIME 2 always requires gzipped format
    output_filename = f"{sample_id}_sequences_L001_R1_001.fastq.gz"
        
    output_path = result.path / output_filename
    # Note: compress_output parameter is ignored - QIIME 2 format requires gzip
    _write_fastq(output_path, all_chunks, sample_id, use_gzip=True)
    
    # Create required MANIFEST file for QIIME 2
    manifest_path = result.path / "MANIFEST"
    _write_manifest(manifest_path, sample_id, output_filename)
    
    # Create required metadata.yml file for QIIME 2
    metadata_path = result.path / "metadata.yml"
    _write_metadata(metadata_path)
    
    # Calculate and log statistics
    total_output_bases = len(all_chunks) * chunk_size
    coverage = total_output_bases / total_input_bases if total_input_bases > 0 else 0
    
    print(f"Processed {sample_id}: {len(sequences_dict)} sequences, "
          f"{total_input_bases:,} input bases -> {len(all_chunks)} chunks, "
          f"{total_output_bases:,} output bases, {coverage:.2f}x coverage")
    
    return result


def _read_fasta(filepath):
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


def _chop_sequence(sequence, chunk_size, slide_bp, max_sequences=None):
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
        
        # Sample random starts
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


def _write_metadata(metadata_file):
    """Write metadata.yml file required by QIIME 2 SingleLanePerSampleSingleEndFastqDirFmt."""
    with open(metadata_file, 'w') as f:
        f.write("phred-offset: 33\n")


def _write_manifest(manifest_file, sample_id, fastq_filename):
    """Write MANIFEST file required by QIIME 2 SingleLanePerSampleSingleEndFastqDirFmt."""
    with open(manifest_file, 'w') as f:
        # Try CSV format instead of TSV
        f.write("sample-id,filename,direction\n")
        f.write(f"{sample_id},{fastq_filename},forward\n")


def _write_fastq(output_file, chunks, sample_id, use_gzip=False):
    """Write chunks to FASTQ format with Illumina-style headers."""
    
    # Choose file opening method based on gzip option
    open_func = gzip.open if use_gzip else open
    mode = 'wt' if use_gzip else 'w'
    
    with open_func(output_file, mode) as f:
        for i, (chunk_id, start, end, chunk) in enumerate(chunks):
            # Create Illumina-style header for QIIME 2 compatibility
            instrument = "SIM"  # Simulator
            run = "001"
            flowcell = "QIIME2"
            lane = "1"
            tile = str(i + 1).zfill(4)
            x_coord = str(start).zfill(5)
            y_coord = str(end).zfill(5)
            read_num = "1"  # Single-end read
            filtered = "N"  # Not filtered
            control = "0"   # Not a control
            index = "ATCG"  # Simple index
            
            seq_id = f"{instrument}:{run}:{flowcell}:{lane}:{tile}:{x_coord}:{y_coord} {read_num}:{filtered}:{control}:{index}"
            quality = "I" * len(chunk)  # High quality scores (Illumina Q40)
            
            f.write(f"@{seq_id}\n")
            f.write(f"{chunk}\n")
            f.write(f"+{chunk_id}\n")  # Keep chunk info in comment line
            f.write(f"{quality}\n")
