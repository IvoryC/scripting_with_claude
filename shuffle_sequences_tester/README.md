# FASTQ Shuffle Verification Tool

A Python command-line tool for verifying that FASTQ sequence shuffling preserves nucleotide composition. This tool compares original and shuffled FASTQ files to ensure that each read maintains the same number of A, T, G, and C nucleotides after shuffling.

## Overview

This verification tool was designed to validate a FASTQ shuffling program that scrambles sequences within individual reads. It ensures that the shuffling process only rearranges nucleotides without adding, removing, or changing any bases.

## Features

- **Nucleotide Count Verification**: Compares A, T, G, C counts between original and shuffled sequences
- **Random Sampling**: Tests a specified number of randomly selected reads
- **Detailed Reporting**: Provides comprehensive progress updates and detailed analysis of one sample read
- **Output Formats**: 
  - PASS/FAIL result to stdout
  - Progress messages to stderr
  - Detailed results table to file
- **Error Handling**: Detects missing reads in shuffled files
- **Flexible Output**: Auto-generates output filenames or accepts custom names

## Installation

No installation required. Simply download the Python script and ensure Python 3.6+ is available.

## Usage

### Basic Usage
```bash
python fastq_verify.py original.fastq shuffled.fastq 1000
```

### With Custom Output File
```bash
python fastq_verify.py original.fastq shuffled.fastq 1000 -o verification_results.tsv
```

### Arguments
- `original_file`: Path to the original FASTQ file (before shuffling)
- `shuffled_file`: Path to the shuffled FASTQ file (after shuffling)
- `num_reads`: Number of reads to test (if greater than available reads, tests all)
- `-o, --output`: Optional output filename for results table

### Output

**Standard Output (stdout):**
- `PASS`: All tested reads maintain nucleotide composition
- `FAIL`: One or more reads failed verification

**Standard Error (stderr):**
- File loading progress
- Read count information
- Processing progress (every 100 reads)
- Detailed report for one randomly selected read
- Final summary statistics

**Output File:**
Tab-separated table with columns:
- `read_name`: Identifier of the read
- `original_sequence`: Original DNA sequence
- `As.original`, `Cs.original`, `Gs.original`, `Ts.original`: Nucleotide counts in original
- `shuffled_sequence`: Shuffled DNA sequence (or "not found")
- `As.shuffled`, `Cs.shuffled`, `Gs.shuffled`, `Ts.shuffled`: Nucleotide counts in shuffled
- `pass.fail`: PASS or FAIL for each read

### Exit Codes
- `0`: All tests passed
- `1`: One or more tests failed

## Example Output

```
$ python fastq_verify.py sample_orig.fastq sample_shuffled.fastq 500
Loading original file: sample_orig.fastq
Loading shuffled file: sample_shuffled.fastq
Original file contains 1000 reads
Shuffled file contains 1000 reads
Testing 500 randomly selected reads

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: read_123
Original sequence: ATCGATCGATCG
Original nucleotide counts: A=3, T=3, G=3, C=3
Shuffled sequence: GCATGCATCATG
Shuffled nucleotide counts: A=3, T=3, G=3, C=3
Result: PASS
==================================================

Progress: 100/500 reads processed
Progress: 200/500 reads processed
Progress: 300/500 reads processed
Progress: 400/500 reads processed
Progress: 500/500 reads processed

=== FINAL SUMMARY ===
Total reads tested: 500
Passed: 500
Failed: 0
Results written to: sample_shuffled_verification_results.tsv

PASS
```

---

## Development Process

### Initial Request
> "I need to create a tool to verify that a tool I've already made is doing what it should. The tool I have takes in a fastq file and shuffles the sequences. It goes through the file one read at a time, and the sequence for each read is scrambled. Now I need a tool that can take in too fastq files (one that was the input to my original tool and one that was an output) and make sure that the number of As, Ts, Cs, and Gs in any given read is the same in the input file and the output file.
>
> I would like this new tool to be run from the command line, and give a pass fail response to standard out.
> It should also print progress messages to standard error, including a detailed report for at least one randomly selected read, for the detailed report includes the name of the read, the original sequence, the number of occurrences of each letter in the original sequence, the shuffled sequence, and the number of occurrences of each letter in the sequence.
>
> I would like it to output a table to a file (the name, for this file should be something it can take as an argument. If the argument is not supplied, then the program should create a file name based on the second input file). This table should include columns for: read name, original sequence, As.original, Cs.original, Gs.original, Ts.original, shuffle sequence, As.shuffled, Cs.shuffled, Gs.shuffled, Ts.shuffled, pass.fail.
>
> The tool should take an argument for the number of reads to test. If the number of reads to test is greater than the number of reads in either of the input files, then test every read. Randomly select this many reads from the first input file. Find the corresponding read (by name) in the second input file. If the corresponding read cannot be found in the second file, that should result in a failure, and the output table should say "not found" instead of the shuffle sequence.
>
> This tool should be written in python and should run under the command line."

### Development Response
The assistant recognized this as a well-specified request with clear requirements and proceeded to create the verification tool. The response included a comprehensive Python script that implemented all requested features including command-line argument parsing, FASTQ file parsing, random read selection, nucleotide counting, progress reporting, detailed analysis of a sample read, and output generation in multiple formats.

**Artifact Created:** `fastq_shuffle_verifier` - Complete Python command-line tool for FASTQ shuffle verification with all requested functionality including error handling for missing reads and flexible output options.

### Documentation Request
> "Please write a README.md files that includes a summary of this tool and how to use it. Also include a summary of the development process. The summary of the development process should include my prompts in quotes exactly as they were given. Include a concise summary of each of your responses, and note when artifacts were created or updated."

### Documentation Response
The assistant created this comprehensive README.md file documenting the tool's functionality, usage instructions, and the complete development process including the original request and development steps.

**Artifact Created:** `readme_fastq_verifier` - Complete documentation including tool overview, usage instructions, examples, and development history.
