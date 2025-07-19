#!/usr/bin/env python3

import sys

def sort_fastq_sequences(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        line_num = 0
        for line in infile:
            line_num += 1
            if line_num % 4 == 2:  # Line 2 (sequence line)
                sorted_sequence = ''.join(sorted(line.strip())) + '\n'
                outfile.write(sorted_sequence)
            else:  # Lines 1, 3, 4 (header, plus, quality)
                outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.fastq output.fastq")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    sort_fastq_sequences(input_file, output_file)
    print(f"Sorted sequences written to {output_file}")
