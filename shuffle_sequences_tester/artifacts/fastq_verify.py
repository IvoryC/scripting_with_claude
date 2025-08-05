#!/usr/bin/env python3
"""
FASTQ Shuffle Verification Tool

Verifies that a FASTQ shuffling tool preserves nucleotide counts by comparing
original and shuffled files.
"""

import argparse
import random
import sys
import os
from collections import Counter
from pathlib import Path


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
    """Count A, T, G, C nucleotides in sequence"""
    counter = Counter(sequence.upper())
    return {
        'A': counter.get('A', 0),
        'T': counter.get('T', 0),
        'G': counter.get('G', 0),
        'C': counter.get('C', 0)
    }


def sequences_match_composition(seq1, seq2):
    """Check if two sequences have the same nucleotide composition"""
    counts1 = count_nucleotides(seq1)
    counts2 = count_nucleotides(seq2)
    return counts1 == counts2


def main():
    parser = argparse.ArgumentParser(
        description="Verify FASTQ shuffling tool preserves nucleotide counts"
    )
    parser.add_argument("original_file", help="Original FASTQ file")
    parser.add_argument("shuffled_file", help="Shuffled FASTQ file")
    parser.add_argument("num_reads", type=int, help="Number of reads to test")
    parser.add_argument("-o", "--output", help="Output table filename")
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if args.output is None:
        shuffled_base = Path(args.shuffled_file).stem
        args.output = f"{shuffled_base}_verification_results.tsv"
    
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
            shuffled_counts = {'A': 0, 'T': 0, 'G': 0, 'C': 0}
            pass_fail = "FAIL"
            failed += 1
        else:
            shuffled_seq = shuffled_reads[read_name]
            original_counts = count_nucleotides(original_seq)
            shuffled_counts = count_nucleotides(shuffled_seq)
            
            if sequences_match_composition(original_seq, shuffled_seq):
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
            'pass_fail': pass_fail
        })
        
        # Print detailed report for selected read
        if read_name == detailed_read:
            print("\n=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===", file=sys.stderr)
            print(f"Read name: {read_name}", file=sys.stderr)
            print(f"Original sequence: {original_seq}", file=sys.stderr)
            print(f"Original nucleotide counts: A={original_counts['A']}, T={original_counts['T']}, G={original_counts['G']}, C={original_counts['C']}", file=sys.stderr)
            print(f"Shuffled sequence: {shuffled_seq}", file=sys.stderr)
            if shuffled_seq != "not found":
                print(f"Shuffled nucleotide counts: A={shuffled_counts['A']}, T={shuffled_counts['T']}, G={shuffled_counts['G']}, C={shuffled_counts['C']}", file=sys.stderr)
            print(f"Result: {pass_fail}", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
    
    # Write results table
    print(f"\nWriting results to: {args.output}", file=sys.stderr)
    with open(args.output, 'w') as f:
        # Write header
        f.write("read_name\toriginal_sequence\tAs.original\tCs.original\tGs.original\tTs.original\t")
        f.write("shuffled_sequence\tAs.shuffled\tCs.shuffled\tGs.shuffled\tTs.shuffled\tpass.fail\n")
        
        # Write data
        for result in results:
            f.write(f"{result['read_name']}\t")
            f.write(f"{result['original_seq']}\t")
            f.write(f"{result['original_counts']['A']}\t")
            f.write(f"{result['original_counts']['C']}\t")
            f.write(f"{result['original_counts']['G']}\t")
            f.write(f"{result['original_counts']['T']}\t")
            f.write(f"{result['shuffled_seq']}\t")
            f.write(f"{result['shuffled_counts']['A']}\t")
            f.write(f"{result['shuffled_counts']['C']}\t")
            f.write(f"{result['shuffled_counts']['G']}\t")
            f.write(f"{result['shuffled_counts']['T']}\t")
            f.write(f"{result['pass_fail']}\n")
    
    # Print final summary to stderr
    print(f"\n=== FINAL SUMMARY ===", file=sys.stderr)
    print(f"Total reads tested: {max_reads}", file=sys.stderr)
    print(f"Passed: {passed}", file=sys.stderr)
    print(f"Failed: {failed}", file=sys.stderr)
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
