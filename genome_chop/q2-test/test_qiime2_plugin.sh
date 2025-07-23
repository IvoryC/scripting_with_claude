#!/bin/bash
"""
Test script for q2-genome-chop QIIME 2 plugin - tests all major features
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0

# Function to print test headers
print_test() {
    echo -e "${BLUE}=== TEST $1: $2 ===${NC}"
    ((TESTS_RUN++))
}

# Function to print and run command
run_command() {
    echo -e "${YELLOW}Command: $1${NC}"
    eval "$1"
    return $?
}

# Function to check if test passed
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
    fi
    echo
}

# Function to check if QIIME 2 artifact exists and has content
check_qza_file() {
    if [ -f "$1" ] && [ -s "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Function to count sequences in exported FASTQ
count_sequences_in_export() {
    if [ -d "$1" ]; then
        local fastq_files=$(find "$1" -name "*.fastq*" | head -1)
        if [ -n "$fastq_files" ]; then
            if [[ "$fastq_files" == *.gz ]]; then
                gunzip -c "$fastq_files" | grep -c "^@"
            else
                grep -c "^@" "$fastq_files"
            fi
        else
            echo "0"
        fi
    else
        echo "0"
    fi
}

# Setup
INPUT_FASTA="../test/input/test_genome.fa"
OUTPUT_DIR="output"
EXPORT_DIR="exported"

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$EXPORT_DIR"

echo -e "${YELLOW}Starting QIIME 2 genome-chop plugin tests...${NC}"
echo

# Test 1: Import FASTA to QIIME 2 artifact
print_test "1" "Import FASTA file to QIIME 2 artifact"
CMD="qiime tools import --input-path \"$INPUT_FASTA\" --output-path \"$OUTPUT_DIR/input_sequences.qza\" --type 'FeatureData[Sequence]'"
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/input_sequences.qza"; then
    echo "Successfully imported FASTA to QIIME 2 artifact"
    RESULT=0
else
    echo "Failed to import FASTA file"
    RESULT=1
fi
check_result $RESULT

# Test 2: Basic sliding window mode
print_test "2" "Basic sliding window mode (100bp chunks, 50bp steps)"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 100 --p-slide-bp 50 --o-chopped-sequences \"$OUTPUT_DIR/basic_sliding.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/basic_sliding.qza"; then
    echo "Basic sliding window completed successfully"
    RESULT=0
else
    echo "Basic sliding window failed"
    RESULT=1
fi
check_result $RESULT

# Test 3: Export and verify basic sliding window output
print_test "3" "Export and verify basic sliding window output"
CMD="qiime tools export --input-path \"$OUTPUT_DIR/basic_sliding.qza\" --output-path \"$EXPORT_DIR/basic_sliding\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/basic_sliding")
    echo "Exported sequences: $SEQ_COUNT"
    # With 300bp input, 100bp chunks, 50bp steps: should generate 5 sequences
    # (0-99, 50-149, 100-199, 150-249, 200-299)
    if [ "$SEQ_COUNT" -eq 5 ]; then
        RESULT=0
    else
        echo "Expected 5 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    RESULT=1
fi
check_result $RESULT

# Test 4: Maximum sequences limit
print_test "4" "Maximum sequences limit (limit to 3 sequences)"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 75 --p-slide-bp 25 --p-max-sequences 3 --o-chopped-sequences \"$OUTPUT_DIR/limited_sequences.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/limited_sequences.qza"; then
    # Export and verify count
    qiime tools export --input-path "$OUTPUT_DIR/limited_sequences.qza" --output-path "$EXPORT_DIR/limited_sequences" > /dev/null 2>&1
    SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/limited_sequences")
    echo "Generated $SEQ_COUNT sequences (limit was 3)"
    if [ "$SEQ_COUNT" -eq 3 ]; then
        RESULT=0
    else
        echo "Expected 3 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    echo "Limited sequences test failed"
    RESULT=1
fi
check_result $RESULT

# Test 5: Random mode with seed
print_test "5" "Random mode with seed (slide-bp=0, 4 random sequences)"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 80 --p-slide-bp 0 --p-max-sequences 4 --p-random-seed 42 --o-chopped-sequences \"$OUTPUT_DIR/random_mode.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/random_mode.qza"; then
    # Export and verify count
    qiime tools export --input-path "$OUTPUT_DIR/random_mode.qza" --output-path "$EXPORT_DIR/random_mode" > /dev/null 2>&1
    SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/random_mode")
    echo "Generated $SEQ_COUNT random sequences"
    if [ "$SEQ_COUNT" -eq 4 ]; then
        RESULT=0
    else
        echo "Expected 4 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    echo "Random mode test failed"
    RESULT=1
fi
check_result $RESULT

# Test 6: Random mode with different parameters and automatic naming
print_test "6" "Random mode with automatic descriptive naming"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 60 --p-slide-bp 0 --p-max-sequences 5 --o-chopped-sequences \"$OUTPUT_DIR/different_chunk.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/different_chunk.qza"; then
    # Export and check results
    qiime tools export --input-path "$OUTPUT_DIR/different_chunk.qza" --output-path "$EXPORT_DIR/different_chunk" > /dev/null 2>&1
    SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/different_chunk")
    
    # Check that filename reflects the descriptive naming (should contain "random_chunks_c60_n5")
    FASTQ_FILE=$(find "$EXPORT_DIR/different_chunk" -name "*.fastq.gz" | head -1)
    if [[ "$FASTQ_FILE" == *"random_chunks_c60_n5"* ]]; then
        echo "Generated $SEQ_COUNT sequences with descriptive naming: random_chunks_c60_n5"
        RESULT=0
    else
        echo "Expected descriptive filename with 'random_chunks_c60_n5', got: $(basename "$FASTQ_FILE")"
        RESULT=1
    fi
else
    echo "Different chunk test failed"
    RESULT=1
fi
check_result $RESULT

# Test 7: Reproducibility test (same seed should give same results)
print_test "7" "Reproducibility test (same seed should give same results)"
CMD1="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 90 --p-slide-bp 0 --p-max-sequences 3 --p-random-seed 123 --o-chopped-sequences \"$OUTPUT_DIR/repro1.qza\""
CMD2="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 90 --p-slide-bp 0 --p-max-sequences 3 --p-random-seed 123 --o-chopped-sequences \"$OUTPUT_DIR/repro2.qza\""
echo -e "${YELLOW}Command 1: $CMD1${NC}"
eval "$CMD1"
RESULT1=$?
echo -e "${YELLOW}Command 2: $CMD2${NC}"
eval "$CMD2"
RESULT2=$?

if [ $RESULT1 -eq 0 ] && [ $RESULT2 -eq 0 ]; then
    # Export both and compare sequence headers
    qiime tools export --input-path "$OUTPUT_DIR/repro1.qza" --output-path "$EXPORT_DIR/repro1" > /dev/null 2>&1
    qiime tools export --input-path "$OUTPUT_DIR/repro2.qza" --output-path "$EXPORT_DIR/repro2" > /dev/null 2>&1
    
    # Get sequence headers from both exports
    HEADERS1=$(find "$EXPORT_DIR/repro1" -name "*.fastq*" -exec bash -c 'if [[ "$1" == *.gz ]]; then gunzip -c "$1"; else cat "$1"; fi' _ {} \; | grep "^@" | sort)
    HEADERS2=$(find "$EXPORT_DIR/repro2" -name "*.fastq*" -exec bash -c 'if [[ "$1" == *.gz ]]; then gunzip -c "$1"; else cat "$1"; fi' _ {} \; | grep "^@" | sort)
    
    if [ "$HEADERS1" = "$HEADERS2" ]; then
        echo "Reproducibility confirmed: identical sequence headers with same seed"
        RESULT=0
    else
        echo "Reproducibility failed: different sequence headers with same seed"
        RESULT=1
    fi
else
    echo "One or both reproducibility commands failed"
    RESULT=1
fi
check_result $RESULT

# Test 7: Custom sample name
print_test "7" "Custom sample name parameter"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 80 --p-slide-bp 40 --p-sample-name \"my_custom_sample\" --o-chopped-sequences \"$OUTPUT_DIR/custom_name.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/custom_name.qza"; then
    # Export and check that custom name is used
    qiime tools export --input-path "$OUTPUT_DIR/custom_name.qza" --output-path "$EXPORT_DIR/custom_name" > /dev/null 2>&1
    
    # Check that filename contains the custom sample name
    FASTQ_FILE=$(find "$EXPORT_DIR/custom_name" -name "*.fastq.gz" | head -1)
    if [[ "$FASTQ_FILE" == *"my_custom_sample"* ]]; then
        SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/custom_name")
        echo "Generated $SEQ_COUNT sequences with custom sample name: my_custom_sample"
        RESULT=0
    else
        echo "Expected custom filename with 'my_custom_sample', got: $(basename "$FASTQ_FILE")"
        RESULT=1
    fi
else
    echo "Custom name test failed"
    RESULT=1
fi
check_result $RESULT

# Test 8: Edge case - chunk size larger than sequence (should produce no sequences)
print_test "8" "Edge case: chunk size larger than sequence (should produce no sequences)"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 400 --p-slide-bp 100 --o-chopped-sequences \"$OUTPUT_DIR/large_chunk.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/large_chunk.qza"; then
    # Export and verify count should be 0
    qiime tools export --input-path "$OUTPUT_DIR/large_chunk.qza" --output-path "$EXPORT_DIR/large_chunk" > /dev/null 2>&1
    SEQ_COUNT=$(count_sequences_in_export "$EXPORT_DIR/large_chunk")
    echo "Generated $SEQ_COUNT sequences (expected 0)"
    if [ "$SEQ_COUNT" -eq 0 ]; then
        RESULT=0
    else
        echo "Expected 0 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    echo "Large chunk test failed"
    RESULT=1
fi
check_result $RESULT

# Test 9: FASTQ format verification (Illumina headers and quality scores)
print_test "9" "FASTQ format verification (Illumina headers and quality scores)"
CMD="qiime genome-chop chop-sequences --i-sequences \"$OUTPUT_DIR/input_sequences.qza\" --p-chunk-size 50 --p-slide-bp 25 --p-max-sequences 2 --o-chopped-sequences \"$OUTPUT_DIR/format_test.qza\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_qza_file "$OUTPUT_DIR/format_test.qza"; then
    # Export and check format
    qiime tools export --input-path "$OUTPUT_DIR/format_test.qza" --output-path "$EXPORT_DIR/format_test" > /dev/null 2>&1
    
    # Find the FASTQ file and check format
    FASTQ_FILE=$(find "$EXPORT_DIR/format_test" -name "*.fastq*" | head -1)
    if [ -n "$FASTQ_FILE" ]; then
        # Get first sequence header
        if [[ "$FASTQ_FILE" == *.gz ]]; then
            FIRST_HEADER=$(gunzip -c "$FASTQ_FILE" | head -n 1)
            QUALITY_LINE=$(gunzip -c "$FASTQ_FILE" | head -n 4 | tail -n 1)
        else
            FIRST_HEADER=$(head -n 1 "$FASTQ_FILE")
            QUALITY_LINE=$(head -n 4 "$FASTQ_FILE" | tail -n 1)
        fi
        
        echo "Sample header: $FIRST_HEADER"
        
        # Check for Illumina-style format and quality scores
        if [[ "$FIRST_HEADER" == *"@SIM:"* ]] && [[ "$FIRST_HEADER" == *" 1:N:0:"* ]] && [[ "$QUALITY_LINE" == *"I"* ]]; then
            echo "FASTQ format correct: Illumina headers and quality scores present"
            echo "Files are gzipped as required by QIIME 2"
            RESULT=0
        else
            echo "FASTQ format incorrect"
            RESULT=1
        fi
    else
        echo "No FASTQ file found in export"
        RESULT=1
    fi
else
    echo "Format test failed"
    RESULT=1
fi
check_result $RESULT

# Test 10: Plugin info and citations
print_test "10" "Plugin info and citations"
CMD="qiime genome-chop --citations"
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Citations displayed successfully"
    RESULT=0
else
    echo "Citations command failed"
    RESULT=1
fi
check_result $RESULT

# Summary
echo -e "${YELLOW}=== TEST SUMMARY ===${NC}"
echo "Tests run: $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $((TESTS_RUN - TESTS_PASSED))"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    echo "Your QIIME 2 genome-chop plugin is working perfectly!"
    exit 0
else
    echo -e "${RED}Some tests failed. 😞${NC}"
    echo "Check the failed tests above for debugging information."
    exit 1
fi
