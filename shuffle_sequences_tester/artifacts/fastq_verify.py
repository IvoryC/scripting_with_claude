#!/usr/bin/env python3
"""
FASTQ Shuffle Verification Tool - fastq_verify.py

Verifies that a FASTQ shuffling tool preserves nucleotide counts by comparing
original and shuffled files.
"""

import argparse
import random
import sys
import os
from collections import Counter
from pathlib import Path

__version__ = "v0.0.20"


def parse_fastq(filename):
    """Parse FASTQ file and return dictionary of {read_name: sequence}"""
    reads = {}
    with open(filename, 'r') as f:
        while True:
            header = f.readline().strip()
            if not header:
                break
            if not header.startswith('@'):
                continue
            
            sequence = f.readline().strip()
            plus = f.readline().strip()
            quality = f.readline().strip()
            
            # Extract read name (remove @ and take first part before space/tab)
            read_name = header[1:].split()[0]
            reads[read_name] = sequence
    
    return reads


def count_nucleotides(sequence):
    """Count A, C, G, T, N, and other nucleotides in sequence"""
    counter = Counter(sequence.upper())
    
    # Count standard nucleotides
    a_count = counter.get('A', 0)
    c_count = counter.get('C', 0)
    g_count = counter.get('G', 0)
    t_count = counter.get('T', 0)
    n_count = counter.get('N', 0)
    
    # Count other characters (anything not A, C, G, T, N)
    standard_bases = {'A', 'C', 'G', 'T', 'N'}
    other_count = sum(count for base, count in counter.items() if base not in standard_bases)
    
    return {
        'A': a_count,
        'C': c_count,
        'G': g_count,
        'T': t_count,
        'N': n_count,
        'other': other_count
    }


def has_single_unique_character(sequence):
    """Check if sequence contains only one unique character"""
    return len(set(sequence.upper())) == 1


def sequences_match_composition(seq1, seq2):
    """Check if two sequences have the same nucleotide composition"""
    counts1 = count_nucleotides(seq1)
    counts2 = count_nucleotides(seq2)
    return counts1 == counts2


def main():
    parser = argparse.ArgumentParser(
        description="Verify FASTQ shuffling tool preserves nucleotide counts"
    )
    parser.add_argument("-v", "--version", action="version", version=f"fastq_verify.py {__version__}")
    parser.add_argument("original_file", help="Original FASTQ file")
    parser.add_argument("shuffled_file", help="Shuffled FASTQ file")
    parser.add_argument("-n", "--num_reads", type=int, default=100, help="Number of reads to test (default: 100)")
    parser.add_argument("-o", "--output", help="Output table filename")
    
    # Check if no arguments provided and show help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(2)
    
    args = parser.parse_args()
    
    # Generate output filename if not provided, or use default naming in specified directory
    if args.output is None:
        shuffled_base = Path(args.shuffled_file).stem
        args.output = f"{shuffled_base}_verification_results.tsv"
    else:
        # Check if output is a directory
        output_path = Path(args.output)
        if output_path.is_dir():
            shuffled_base = Path(args.shuffled_file).stem
            default_filename = f"{shuffled_base}_verification_results.tsv"
            args.output = str(output_path / default_filename)
    
    print(f"Loading original file: {args.original_file}", file=sys.stderr)
    original_reads = parse_fastq(args.original_file)
    
    print(f"Loading shuffled file: {args.shuffled_file}", file=sys.stderr)
    shuffled_reads = parse_fastq(args.shuffled_file)
    
    print(f"Original file contains {len(original_reads)} reads", file=sys.stderr)
    print(f"Shuffled file contains {len(shuffled_reads)} reads", file=sys.stderr)
    
    # Determine number of reads to test
    max_reads = min(len(original_reads), args.num_reads)
    if args.num_reads > len(original_reads):
        print(f"Requested {args.num_reads} reads, but only {len(original_reads)} available. Testing all reads.", file=sys.stderr)
    
    # Randomly select reads to test
    read_names_to_test = random.sample(list(original_reads.keys()), max_reads)
    
    print(f"Testing {max_reads} randomly selected reads", file=sys.stderr)
    
    # Select one read for detailed report
    detailed_read = random.choice(read_names_to_test)
    
    # Track results
    results = []
    passed = 0
    failed = 0
    identical_sequences = 0
    not_checked_for_identity = 0
    checked_and_different = 0
    
    # Test each selected read
    for i, read_name in enumerate(read_names_to_test):
        if (i + 1) % 100 == 0:
            print(f"Progress: {i + 1}/{max_reads} reads processed", file=sys.stderr)
        
        original_seq = original_reads[read_name]
        
        # Check if read exists in shuffled file
        if read_name not in shuffled_reads:
            print(f"WARNING: Read {read_name} not found in shuffled file", file=sys.stderr)
            shuffled_seq = "not found"
            original_counts = count_nucleotides(original_seq)
            shuffled_counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0, 'N': 0, 'other': 0}
            sequences_identical = "N/A"
            pass_fail = "FAIL"
            failed += 1
        else:
            shuffled_seq = shuffled_reads[read_name]
            original_counts = count_nucleotides(original_seq)
            shuffled_counts = count_nucleotides(shuffled_seq)
            
            # Check for composition match first
            composition_matches = sequences_match_composition(original_seq, shuffled_seq)
            
            # Check if sequences are identical, but only if more than one unique character
            if has_single_unique_character(original_seq):
                sequences_identical = "N/A"
                not_checked_for_identity += 1
                # Don't fail for identity when only one unique character
                if composition_matches:
                    pass_fail = "PASS"
                    passed += 1
                else:
                    pass_fail = "FAIL"
                    failed += 1
            else:
                # Check if sequences are identical
                if original_seq == shuffled_seq:
                    sequences_identical = "TRUE"
                    identical_sequences += 1
                    pass_fail = "FAIL"  # Identical sequences should fail
                    failed += 1
                else:
                    sequences_identical = "FALSE"
                    checked_and_different += 1
                    if composition_matches:
                        pass_fail = "PASS"
                        passed += 1
                    else:
                        pass_fail = "FAIL"
                        failed += 1
        
        # Store result
        results.append({
            'read_name': read_name,
            'original_seq': original_seq,
            'original_counts': original_counts,
            'shuffled_seq': shuffled_seq,
            'shuffled_counts': shuffled_counts,
            'sequences_identical': sequences_identical,
            'pass_fail': pass_fail
        })
        
        # Print detailed report for selected read
        if read_name == detailed_read:
            print("\n=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===", file=sys.stderr)
            print(f"Read name: {read_name}", file=sys.stderr)
            print(f"Original sequence: {original_seq}", file=sys.stderr)
            print(f"Original nucleotide counts: A={original_counts['A']}, C={original_counts['C']}, G={original_counts['G']}, T={original_counts['T']}, N={original_counts['N']}, other={original_counts['other']}", file=sys.stderr)
            print(f"Shuffled sequence: {shuffled_seq}", file=sys.stderr)
            if shuffled_seq != "not found":
                print(f"Shuffled nucleotide counts: A={shuffled_counts['A']}, C={shuffled_counts['C']}, G={shuffled_counts['G']}, T={shuffled_counts['T']}, N={shuffled_counts['N']}, other={shuffled_counts['other']}", file=sys.stderr)
                print(f"Sequences identical: {sequences_identical}", file=sys.stderr)
            print(f"Result: {pass_fail}", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
    
    # Write results table
    print(f"\nWriting results to: {args.output}", file=sys.stderr)
    with open(args.output, 'w') as f:
        # Write header
        f.write("read_name\toriginal_sequence\tAs.original\tCs.original\tGs.original\tTs.original\tNs.original\tother.original\t")
        f.write("shuffled_sequence\tAs.shuffled\tCs.shuffled\tGs.shuffled\tTs.shuffled\tNs.shuffled\tother.shuffled\tsequences_identical\tpass.fail\n")
        
        # Write data
        for result in results:
            f.write(f"{result['read_name']}\t")
            f.write(f"{result['original_seq']}\t")
            f.write(f"{result['original_counts']['A']}\t")
            f.write(f"{result['original_counts']['C']}\t")
            f.write(f"{result['original_counts']['G']}\t")
            f.write(f"{result['original_counts']['T']}\t")
            f.write(f"{result['original_counts']['N']}\t")
            f.write(f"{result['original_counts']['other']}\t")
            f.write(f"{result['shuffled_seq']}\t")
            f.write(f"{result['shuffled_counts']['A']}\t")
            f.write(f"{result['shuffled_counts']['C']}\t")
            f.write(f"{result['shuffled_counts']['G']}\t")
            f.write(f"{result['shuffled_counts']['T']}\t")
            f.write(f"{result['shuffled_counts']['N']}\t")
            f.write(f"{result['shuffled_counts']['other']}\t")
            f.write(f"{result['sequences_identical']}\t")
            f.write(f"{result['pass_fail']}\n")
    
    # Print final summary to stderr
    print(f"\n=== FINAL SUMMARY ===", file=sys.stderr)
    print(f"Total reads tested: {max_reads}", file=sys.stderr)
    print(f"Passed: {passed}", file=sys.stderr)
    print(f"Failed: {failed}", file=sys.stderr)
    
    # If there were identical sequences, provide detailed breakdown
    if identical_sequences > 0:
        print(f"\n=== IDENTITY CHECK SUMMARY ===", file=sys.stderr)
        print(f"Reads not checked for identity (single unique character): {not_checked_for_identity}", file=sys.stderr)
        print(f"Reads found to be identical to original: {identical_sequences}", file=sys.stderr)
        print(f"Reads checked and found different from original: {checked_and_different}", file=sys.stderr)
        print(f"NOTE: Identical sequences are considered test failures", file=sys.stderr)
    
    print(f"Results written to: {args.output}", file=sys.stderr)
    
    # Print pass/fail result to stdout
    if failed == 0:
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
