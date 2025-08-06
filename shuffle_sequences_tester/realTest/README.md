# Real Test Results



## From the WGS isolates project

Tested 5 examples, 1000 reads each (or all in reads in the file). 

All passed.

The script used to do the shuffle for these was "shuffle_v3.py".

### Sample 10

**python fastq_verify_v32.py $IN1 $IN2 -n 1000 -o realResults/**
```
Loading original file: ../../01_MergePairs/output/10_S228_L008_Merged_001.fastq.gz
Loading shuffled file: ../../02_ShuffleSequences/output/10_S228_L008_Merged_001.fastq_shuffle_1mer.gz.gz
Original file contains 7746651 reads
Shuffled file contains 7746651 reads
Testing 1000 randomly selected reads
Progress: 100/1000 reads processed
Progress: 200/1000 reads processed
Progress: 300/1000 reads processed
Progress: 400/1000 reads processed
Progress: 500/1000 reads processed

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: LH00373:306:232KJYLT3:8:2281:24908:17301
Original sequence: CCGCAGTACAATGCTGCCAAAGGTCATATGACCAAGTGCGATGGCTGTCATGACCGCGTGGCCGACGGCAAAAAGCCCATCTGCGTCGAGTCCTGTCCGCTGCGCGCGCTGGACTTTGGTCCAATTGATGAGCTGCGCAAAAAGCACGGTGAACTGGCGGCGGTCGCTCCGCTGCCAGGTGCGCACTTCACCAAACCGAGCATTGTGATCAAACCCAACGCCAATAGCCGCCCGACCGGGGATACCACGGGTTATCTGGCGAATCCGCAGGAGGTGTAACAT
Original nucleotide counts: A=65, C=85, G=82, T=50, N=0, other=0
Shuffled sequence: AGCAGGCGCAGCCCGGGGTGCCGTCTCACGTGACAAAGGGGCGAACTTCCACATCCGGCAGCCCTGAGAACGGAACCGCCTCATGCAGCAGTTAGCTCAACCCGCCTGAATCTTTGACGCCCTGTGCCTGGCCGGTGGATACCGTTAACCTGGTTACATGGAGCATCACGCGAGGATGCCCGGGACCCACGGGTGTCGACCCATCCAGGCGCCGAACCCAGCAAACGGAATGAGCTCGGTTATGTGAGTCATAAACCGACTATTATATTGGTAGGGCCATAG
Shuffled nucleotide counts: A=65, C=85, G=82, T=50, N=0, other=0
Sequences identical: FALSE
Result: PASS
==================================================
Progress: 600/1000 reads processed
Progress: 700/1000 reads processed
Progress: 800/1000 reads processed
Progress: 900/1000 reads processed
Progress: 1000/1000 reads processed

Writing results to: realResults/10_S228_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv

=== FINAL SUMMARY ===
Total reads tested: 1000
Passed: 1000
Failed: 0
Results written to: realResults/10_S228_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv
PASS
```

### Sample 11

**python fastq_verify_v32.py $IN1 $IN2 -n 1000 -o realResults/**
```
Loading original file: ../../01_MergePairs/output/11_S229_L008_Merged_001.fastq.gz
Loading shuffled file: ../../02_ShuffleSequences/output/11_S229_L008_Merged_001.fastq_shuffle_1mer.gz.gz
Original file contains 8908593 reads
Shuffled file contains 8908593 reads
Testing 1000 randomly selected reads
Progress: 100/1000 reads processed
Progress: 200/1000 reads processed
Progress: 300/1000 reads processed

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: LH00373:306:232KJYLT3:8:1262:6667:10079
Original sequence: CACCCAGGCTACCCAGGTTTGCTACTTTATCAAGCAGAATAACTTGCATTACCTTATCCTCTCAAAGTCGTATTAATGGACCGTGACCGATTACTGATGACGATCAGTGTACGGCAGCAGGGACAGGT
Original nucleotide counts: A=35, C=32, G=28, T=33, N=0, other=0
Shuffled sequence: ATACTACAAGAAGCTTCACCGAATTCGCTCATACAATTGATCCGTTGGGGCTTATTTCACGTACCGAGTACTCATATGTCAGCTGCGCTTACAAAGCCGAACGCGGGTGCCAGCTAGAGATATTTCAG
Shuffled nucleotide counts: A=35, C=32, G=28, T=33, N=0, other=0
Sequences identical: FALSE
Result: PASS
==================================================
Progress: 400/1000 reads processed
Progress: 500/1000 reads processed
Progress: 600/1000 reads processed
Progress: 700/1000 reads processed
Progress: 800/1000 reads processed
Progress: 900/1000 reads processed
Progress: 1000/1000 reads processed

Writing results to: realResults/11_S229_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv

=== FINAL SUMMARY ===
Total reads tested: 1000
Passed: 1000
Failed: 0
Results written to: realResults/11_S229_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv
PASS
```

### Sample 4

**python fastq_verify_v32.py $IN1 $IN2 -n 1000 -o realResults/**
```
Loading original file: ../../01_MergePairs/output/4_S222_L008_Merged_001.fastq.gz
Loading shuffled file: ../../02_ShuffleSequences/output/4_S222_L008_Merged_001.fastq_shuffle_1mer.gz.gz
Original file contains 10237461 reads
Shuffled file contains 10237461 reads
Testing 1000 randomly selected reads
Progress: 100/1000 reads processed
Progress: 200/1000 reads processed
Progress: 300/1000 reads processed
Progress: 400/1000 reads processed
Progress: 500/1000 reads processed

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: LH00373:306:232KJYLT3:8:1186:46208:16244
Original sequence: ACCGCACGCTGCCCGTTCGTTTCGATCAGGCGAGGCGTTGATATTCCTTCGCTATCTCGCAGGCCAGTACGGCGTTGTTAAACACCAGTTGGATGTTGGACTTCAGGCTGTCGCCTCCGGTTAATTCAGCAACGCGCGCCAGCAGGAACGGCGTGCTCTCTTTACCGATAACGCCCTGCTCTTCCGCTTCCCGGACGGCCTGGTCAATCGCCGCATTGATTTTCTCTTCCGCCATGGCGTAGGTTTCCGGGATTGGATTGGCGACCACCAGACCTCCGTTC
Original nucleotide counts: A=45, C=89, G=74, T=73, N=0, other=0
Shuffled sequence: ATCCCTCCATCCCTTATTTAGTCTGACCGCCTGGTCGCTCTTGGGTCGTAACGGAACCGCCCGATCACGACGGTATAACTCCCCTTTTCGTGCAGTTCGTGGGCCTGTCCTACCAGGGCCTTGCCTCCCCTCACTCGGATGCGGCGTCACTACAAGGCGGCTGTCCGCGCCCTTTGGTTTCTGTGAAGGGTTGTTGAGCCAAAATGCGCAGGCCGCTGTGTGCCGTCTTCAGGGTGAAAAGTATCACTTCGGCTGCTGAGACTCGCCAACACGTTGATCCT
Shuffled nucleotide counts: A=45, C=89, G=74, T=73, N=0, other=0
Sequences identical: FALSE
Result: PASS
==================================================
Progress: 600/1000 reads processed
Progress: 700/1000 reads processed
Progress: 800/1000 reads processed
Progress: 900/1000 reads processed
Progress: 1000/1000 reads processed

Writing results to: realResults/4_S222_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv

=== FINAL SUMMARY ===
Total reads tested: 1000
Passed: 1000
Failed: 0
Results written to: realResults/4_S222_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv
PASS
```

### Sample 30

**python fastq_verify_v32.py $IN1 $IN2 -n 1000 -o realResults/**
```
Loading original file: ../../01_MergePairs/output/30_S249_L008_Merged_001.fastq.gz
Loading shuffled file: ../../02_ShuffleSequences/output/30_S249_L008_Merged_001.fastq_shuffle_1mer.gz.gz
Original file contains 7608921 reads
Shuffled file contains 7608921 reads
Testing 1000 randomly selected reads
Progress: 100/1000 reads processed
Progress: 200/1000 reads processed
Progress: 300/1000 reads processed
Progress: 400/1000 reads processed
Progress: 500/1000 reads processed
Progress: 600/1000 reads processed

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: LH00373:306:232KJYLT3:8:1143:44146:22986
Original sequence: ACCATCTTCCGGCGCGCGGCGGCCAAAGCAGCTTGCCTTGCTCTCGTCCTGCGCGGTCTCGCTGAAGGTGCCGTTAAGGATGCCCGGCAGCGCATCGCGCAGCAGCGTCTGTGCCGTCGCGTTCAGCTTTTGATGCAGCTGCAGCGCGGTATCGTCCGCATCAATAGCGACCTTCTGCTGCGCCACGATAGCGCCCGCATCCGCACGGCGCACCATGCGGTGCAGCGTCACGCCCGTTTCCGTTTCACCGTTCACCAGCACCCAGTTTAGCGGGGCGCGGCCACGGTAGGC
Original nucleotide counts: A=42, C=104, G=88, T=57, N=0, other=0
Shuffled sequence: TATCCATCCGGCTGGTGCGATTAGCCAGGGTGCGGGCGCGACGTTTGTCGTTTACGAATTGGCCGGGACCCCATCGTCACGCTAGTGCGGGTCCTGGCTCACGACTCGCGCTGAGCGTAAGAACTGCCCTCGGCCAGCGGGCTCCGGCCCCGCAACCAGCGATTCCAATCAAGGTCGCGCTTGCAACGCAGCGCCCCCAGCCAAGCTCCTGTAGATTGTGCCCCGCGGTGACGCCCTGGCTACTCGCCCAGGCTCGTTCCTCATCGCTGTTCTTCGCGCCGGTGCACGCGG
Shuffled nucleotide counts: A=42, C=104, G=88, T=57, N=0, other=0
Sequences identical: FALSE
Result: PASS
==================================================
Progress: 700/1000 reads processed
Progress: 800/1000 reads processed
Progress: 900/1000 reads processed
Progress: 1000/1000 reads processed

Writing results to: realResults/30_S249_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv

=== FINAL SUMMARY ===
Total reads tested: 1000
Passed: 1000
Failed: 0
Results written to: realResults/30_S249_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv
PASS
```

### ExNeg4

Note that this example only had 103 reads.

**python fastq_verify_v32.py $IN1 $IN2 -n 1000 -o realResults/**
```
Loading original file: ../../01_MergePairs/output/ExNeg4_S301_L008_Merged_001.fastq.gz
Loading shuffled file: ../../02_ShuffleSequences/output/ExNeg4_S301_L008_Merged_001.fastq_shuffle_1mer.gz.gz
Original file contains 103 reads
Shuffled file contains 103 reads
Requested 1000 reads, but only 103 available. Testing all reads.
Testing 103 randomly selected reads

=== DETAILED REPORT FOR RANDOMLY SELECTED READ ===
Read name: LH00373:306:232KJYLT3:8:1184:39533:3274
Original sequence: CAGTTGCGGTGACAGCGAGAGCAGCTTTGCTCTGCACGACTGTGTTTGCAGAACGCAGTGGGCTGATGATGGCATGCATGATGTCGTGATTCTGTATGTTCAGGCGCAGGGGCTCCTGCATGGCCATGTTTGTTAATAC
Original nucleotide counts: A=26, C=29, G=45, T=39, N=0, other=0
Shuffled sequence: TGGTTAACGGTAGGCCGAAAATGGCCCTGGCCCCGTGTGAAGAGGGCACCTTAGTGGGATCTTCTGGATAGCTGCTGGGTAGCTAGTCAAGATATGCACATGAGTCGTCATTGTTCCTGTTCGGGGATCGTGCCTTTGT
Shuffled nucleotide counts: A=26, C=29, G=45, T=39, N=0, other=0
Sequences identical: FALSE
Result: PASS
==================================================
Progress: 100/103 reads processed

Writing results to: realResults/ExNeg4_S301_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv

=== FINAL SUMMARY ===
Total reads tested: 103
Passed: 103
Failed: 0
Results written to: realResults/ExNeg4_S301_L008_Merged_001.fastq_shuffle_1mer.gz_verification_results.tsv
PASS
```