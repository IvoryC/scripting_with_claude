#!/bin/bash
"""
Test script for genome-chop.py - tests all major features
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

# Function to count sequences in FASTQ file (handles both regular and gzipped)
count_sequences() {
    if [ -f "$1" ]; then
        if [[ "$1" == *.gz ]]; then
            gunzip -c "$1" | grep -c "^@"
        else
            grep -c "^@" "$1"
        fi
    else
        echo "0"
    fi
}

# Function to check if file exists and has content (handles both regular and gzipped)
check_file() {
    if [ -f "$1" ] && [ -s "$1" ]; then
        return 0
    else
        return 1
    fi
}

# Setup
SCRIPT="../script/genome-chop.py"
INPUT="input/test_genome.fa"
OUTPUT_DIR="output"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${YELLOW}Starting genome-chop.py feature tests...${NC}"
echo

# Test 1: Basic sliding window mode
print_test "1" "Basic sliding window mode (50bp chunks, 25bp steps)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 50 -s 25 -o \"$OUTPUT_DIR/test1.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test1.fastq")
    echo "Generated $SEQ_COUNT sequences"
    # With 300bp input, 50bp chunks, 25bp steps: should generate 11 sequences
    # (0-49, 25-74, 50-99, 75-124, 100-149, 125-174, 150-199, 175-224, 200-249, 225-274, 250-299)
    if [ "$SEQ_COUNT" -eq 11 ]; then
        RESULT=0
    else
        echo "Expected 11 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
fi
check_result $RESULT

# Test 2: Maximum sequences limit
print_test "2" "Maximum sequences limit (limit to 5 sequences)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 50 -s 25 -n 5 -o \"$OUTPUT_DIR/test2.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test2.fastq")
    echo "Generated $SEQ_COUNT sequences"
    if [ "$SEQ_COUNT" -eq 5 ]; then
        RESULT=0
    else
        echo "Expected 5 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
fi
check_result $RESULT

# Test 3: Random mode
print_test "3" "Random mode (slide-bp = 0, 8 random sequences)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 60 -s 0 -n 8 -o \"$OUTPUT_DIR/test3.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test3.fastq")
    echo "Generated $SEQ_COUNT sequences"
    if [ "$SEQ_COUNT" -eq 8 ]; then
        RESULT=0
    else
        echo "Expected 8 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
fi
check_result $RESULT

# Test 4: Large chunks (bigger than slide)
print_test "4" "Large chunks with small slide (100bp chunks, 20bp steps)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 100 -s 20 -o \"$OUTPUT_DIR/test4.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test4.fastq")
    echo "Generated $SEQ_COUNT sequences"
    # With 300bp input, 100bp chunks, 20bp steps: should generate 11 sequences
    # (0-99, 20-119, 40-139, 60-159, 80-179, 100-199, 120-219, 140-239, 160-259, 180-279, 200-299)
    if [ "$SEQ_COUNT" -eq 11 ]; then
        RESULT=0
    else
        echo "Expected 11 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
fi
check_result $RESULT

# Test 5: Sequence naming format (Illumina-style headers)
print_test "5" "Illumina-style sequence headers"
python3 "$SCRIPT" -i "$INPUT" -c 30 -s 30 -n 3 -o "$OUTPUT_DIR/test5.fastq"
RESULT=$?
if [ $RESULT -eq 0 ] && check_file "$OUTPUT_DIR/test5.fastq"; then
    # Check if the first sequence has the correct Illumina-style naming format
    FIRST_SEQ=$(head -n 1 "$OUTPUT_DIR/test5.fastq")
    if [[ "$FIRST_SEQ" == *"@SIM:001:INSILICO"* ]] && [[ "$FIRST_SEQ" == *" 1:N:0:ATCG"* ]]; then
        echo "Correct Illumina-style format found: $FIRST_SEQ"
        RESULT=0
    else
        echo "Incorrect header format: $FIRST_SEQ"
        RESULT=1
    fi
else
    RESULT=1
fi
check_result $RESULT

# Test 6: FASTQ format verification (Illumina-style with genomic coordinates)
print_test "6" "FASTQ format verification (Illumina headers, genomic coordinates, quality scores)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 40 -s 40 -n 2 -o \"$OUTPUT_DIR/test6.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_file "$OUTPUT_DIR/test6.fastq"; then
    # Check line count (should be 4 lines per sequence)
    LINE_COUNT=$(wc -l < "$OUTPUT_DIR/test6.fastq")
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test6.fastq")
    EXPECTED_LINES=$((SEQ_COUNT * 4))
    
    if [ "$LINE_COUNT" -eq "$EXPECTED_LINES" ]; then
        # Check if quality line exists and has correct content
        QUALITY_LINE=$(sed -n '4p' "$OUTPUT_DIR/test6.fastq")
        # Check if comment line has genomic coordinates
        COMMENT_LINE=$(sed -n '3p' "$OUTPUT_DIR/test6.fastq")
        if [[ "$QUALITY_LINE" == *"I"* ]] && [[ "$COMMENT_LINE" == *"test_genome:"* ]]; then
            echo "FASTQ format correct: $SEQ_COUNT sequences, $LINE_COUNT lines"
            echo "Quality scores and genomic coordinates present"
            RESULT=0
        else
            echo "Quality scores or genomic coordinates incorrect"
            echo "Quality: $QUALITY_LINE"
            echo "Comment: $COMMENT_LINE"
            RESULT=1
        fi
    else
        echo "Line count incorrect: expected $EXPECTED_LINES, got $LINE_COUNT"
        RESULT=1
    fi
else
    RESULT=1
fi
check_result $RESULT

# Test 7: Help functionality
print_test "7" "Help functionality"
CMD="python3 \"$SCRIPT\" --help > \"$OUTPUT_DIR/help_output.txt\" 2>&1"
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && grep -q "Examples:" "$OUTPUT_DIR/help_output.txt"; then
    echo "Help output generated successfully"
    RESULT=0
else
    echo "Help output failed or incomplete"
    RESULT=1
fi
check_result $RESULT

# Test 8: Default output filename
print_test "8" "Default output filename generation"
# Remove any existing default output file
rm -f "input/test_genome_chopped.fastq"
cd input
python3 "../../script/genome-chop.py" -i "test_genome.fa" -c 50 -s 50 -n 3
RESULT=$?
cd ..
if [ $RESULT -eq 0 ] && check_file "input/test_genome_chopped.fastq"; then
    echo "Default output file created successfully"
    RESULT=0
else
    echo "Default output file not created"
    RESULT=1
fi
check_result $RESULT

# Test 9: Edge case - chunk size larger than sequence
print_test "9" "Edge case: chunk size larger than sequence (400bp chunks on 300bp sequence)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 400 -s 100 -o \"$OUTPUT_DIR/test9.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test9.fastq")
    echo "Generated $SEQ_COUNT sequences"
    # Should generate 0 sequences since chunk is larger than input
    if [ "$SEQ_COUNT" -eq 0 ]; then
        RESULT=0
    else
        echo "Expected 0 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    RESULT=1
fi
check_result $RESULT

# Test 10: Coverage statistics output
print_test "10" "Coverage statistics in output"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 50 -s 25 -n 5 -o \"$OUTPUT_DIR/test10.fastq\""
OUTPUT=$(run_command "$CMD" 2>&1)
RESULT=$?
if [ $RESULT -eq 0 ] && echo "$OUTPUT" | grep -q "Average coverage:" && echo "$OUTPUT" | grep -q "Total input bases:" && echo "$OUTPUT" | grep -q "Total output bases:"; then
    echo "Coverage statistics found in output"
    RESULT=0
else
    echo "Coverage statistics missing from output"
    RESULT=1
fi
check_result $RESULT

# Test 11: Kraken compatibility (direction indicator and Illumina format)
print_test "11" "Kraken compatibility (direction indicator present)"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 75 -s 50 -n 3 -o \"$OUTPUT_DIR/test11.fastq\""
run_command "$CMD"
RESULT=$?
if [ $RESULT -eq 0 ] && check_file "$OUTPUT_DIR/test11.fastq"; then
    # Check if all sequence headers have direction indicators
    HEADERS=$(grep "^@" "$OUTPUT_DIR/test11.fastq")
    DIRECTION_COUNT=$(echo "$HEADERS" | grep -c " 1:N:0:")
    SEQ_COUNT=$(count_sequences "$OUTPUT_DIR/test11.fastq")
    
    if [ "$DIRECTION_COUNT" -eq "$SEQ_COUNT" ]; then
        echo "All $SEQ_COUNT sequences have direction indicators"
        echo "Sample header: $(echo "$HEADERS" | head -n 1)"
        RESULT=0
    else
        echo "Missing direction indicators: found $DIRECTION_COUNT, expected $SEQ_COUNT"
        RESULT=1
    fi
else
    RESULT=1
fi
check_result $RESULT

# Test 12: Directory output functionality
print_test "12" "Directory output functionality"
mkdir -p "$OUTPUT_DIR/subdir"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 60 -s 30 -n 4 -o \"$OUTPUT_DIR/subdir/\""
run_command "$CMD"
RESULT=$?
EXPECTED_FILE="$OUTPUT_DIR/subdir/test_genome_chopped.fastq"
if [ $RESULT -eq 0 ] && check_file "$EXPECTED_FILE"; then
    SEQ_COUNT=$(count_sequences "$EXPECTED_FILE")
    echo "Directory output created: $EXPECTED_FILE"
    echo "Generated $SEQ_COUNT sequences"
    if [ "$SEQ_COUNT" -eq 4 ]; then
        RESULT=0
    else
        echo "Expected 4 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    echo "Directory output file not created at $EXPECTED_FILE"
    RESULT=1
fi
check_result $RESULT

# Test 13: Gzip compression functionality
print_test "13" "Gzip compression functionality"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 50 -s 25 -n 6 -z -o \"$OUTPUT_DIR/test13.fastq\""
run_command "$CMD"
RESULT=$?
EXPECTED_FILE="$OUTPUT_DIR/test13.fastq.gz"
if [ $RESULT -eq 0 ] && check_file "$EXPECTED_FILE"; then
    SEQ_COUNT=$(count_sequences "$EXPECTED_FILE")
    echo "Gzip output created: $EXPECTED_FILE"
    echo "Generated $SEQ_COUNT sequences"
    
    # Verify it's actually gzipped
    if file "$EXPECTED_FILE" | grep -q "gzip"; then
        echo "File is properly gzipped"
        if [ "$SEQ_COUNT" -eq 6 ]; then
            RESULT=0
        else
            echo "Expected 6 sequences, got $SEQ_COUNT"
            RESULT=1
        fi
    else
        echo "File is not gzipped"
        RESULT=1
    fi
else
    echo "Gzip output file not created at $EXPECTED_FILE"
    RESULT=1
fi
check_result $RESULT

# Test 14: Combined directory output and gzip
print_test "14" "Combined directory output and gzip compression"
mkdir -p "$OUTPUT_DIR/gzip_test"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 80 -s 40 -n 3 -z -o \"$OUTPUT_DIR/gzip_test/\""
run_command "$CMD"
RESULT=$?
EXPECTED_FILE="$OUTPUT_DIR/gzip_test/test_genome_chopped.fastq.gz"
if [ $RESULT -eq 0 ] && check_file "$EXPECTED_FILE"; then
    SEQ_COUNT=$(count_sequences "$EXPECTED_FILE")
    echo "Combined directory + gzip output created: $EXPECTED_FILE"
    echo "Generated $SEQ_COUNT sequences"
    
    # Verify it's gzipped and has correct count
    if file "$EXPECTED_FILE" | grep -q "gzip" && [ "$SEQ_COUNT" -eq 3 ]; then
        RESULT=0
    else
        echo "File verification failed"
        RESULT=1
    fi
else
    echo "Combined output file not created at $EXPECTED_FILE"
    RESULT=1
fi
check_result $RESULT

# Test 15: Gzip with random mode
print_test "15" "Gzip with random mode"
CMD="python3 \"$SCRIPT\" -i \"$INPUT\" -c 70 -s 0 -n 5 -z -o \"$OUTPUT_DIR/random_gzip.fastq\""
run_command "$CMD"
RESULT=$?
EXPECTED_FILE="$OUTPUT_DIR/random_gzip.fastq.gz"
if [ $RESULT -eq 0 ] && check_file "$EXPECTED_FILE"; then
    SEQ_COUNT=$(count_sequences "$EXPECTED_FILE")
    echo "Random mode gzip output created: $EXPECTED_FILE"
    echo "Generated $SEQ_COUNT sequences"
    
    if [ "$SEQ_COUNT" -eq 5 ]; then
        RESULT=0
    else
        echo "Expected 5 sequences, got $SEQ_COUNT"
        RESULT=1
    fi
else
    echo "Random mode gzip file not created at $EXPECTED_FILE"
    RESULT=1
fi
check_result $RESULT
echo "Tests run: $TESTS_RUN"
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $((TESTS_RUN - TESTS_PASSED))"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. 😞${NC}"
    exit 1
fi
