#!/bin/bash

# Test script for minimum_proportion.R
# This script runs multiple test cases to verify all features

echo "========================================="
echo "Testing minimum_proportion.R script"
echo "========================================="

# # Create the test data file
# # Strategic data designed to test different scenarios:
# # field_sample_01: One dominant taxon (cockroach: 9950/10000 = 99.5%)
# # field_sample_02: Very dominant taxon (weevil: 9999/10000 = 99.99%)
# # field_sample_03: Two taxa above threshold (ladybug: 85%, grasshopper: 15%)
# # field_sample_04: All zeros (tests zero-count handling)
# # field_sample_05: Multiple taxa, none dominant (tests removal)
# # field_sample_06: Single dominant taxon (thrips: 100%)
# # field_sample_07: All equal counts (tests equal distribution)
# # field_sample_08: Single count (tests minimum case)
# # field_sample_09: Multiple taxa, some dominant
# # field_sample_10: Near-dominant taxon (ladybug: 99.99%)

# echo "Creating test data file: hypothetical_bug_counts.txt"
# cat > hypothetical_bug_counts.txt << 'EOF'
# sample_id	ladybug	grasshopper	cricket	beetle	ant	butterfly	dragonfly	bee	wasp	moth	fly	mosquito	termite	aphid	caterpillar	spider	tick	flea	mite	cockroach	praying_mantis	cicada	firefly	weevil	thrips
# field_sample_01	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	9950	0	0	0	0	50
# field_sample_02	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	9999	1
# field_sample_03	8500	1500	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
# field_sample_04	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
# field_sample_05	3000	2000	2000	2000	1000	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
# field_sample_06	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	10000
# field_sample_07	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100	100
# field_sample_08	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	1
# field_sample_09	5000	3000	2000	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0
# field_sample_10	9999	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	1
# EOF

# echo "Test data file created successfully."
# echo ""

# Test 1: Basic functionality with default parameters (0.99)
echo "TEST 1: Basic functionality with default proportion (0.99)"
echo "Command: Rscript minimum_proportion.R hypothetical_bug_counts.txt"
Rscript minimum_proportion.R hypothetical_bug_counts.txt
echo "Expected output file: hypothetical_bug_counts_minProportion-0.99.txt"
echo "Check if file exists:"
ls -la hypothetical_bug_counts_minProportion-0.99.txt 2>/dev/null && echo "✓ File created" || echo "✗ File not found"
echo ""

# Test 2: Custom proportion (0.5)
echo "TEST 2: Custom proportion (0.5)"
echo "Command: Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.5"
Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.5
echo "Expected output file: hypothetical_bug_counts_minProportion-0.5.txt"
echo "Check if file exists:"
ls -la hypothetical_bug_counts_minProportion-0.5.txt 2>/dev/null && echo "✓ File created" || echo "✗ File not found"
echo ""

# Test 3: Custom proportion with high precision (0.999)
echo "TEST 3: Custom proportion with high precision (0.999)"
echo "Command: Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.999"
Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.999
echo "Expected output file: hypothetical_bug_counts_minProportion-0.999.txt"
echo "Check if file exists:"
ls -la hypothetical_bug_counts_minProportion-0.999.txt 2>/dev/null && echo "✓ File created" || echo "✗ File not found"
echo ""

# Test 4: Custom output file
echo "TEST 4: Custom output file specification"
echo "Command: Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.8 custom_output.txt"
Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.8 custom_output.txt
echo "Expected output file: custom_output.txt"
echo "Check if file exists:"
ls -la custom_output.txt 2>/dev/null && echo "✓ File created" || echo "✗ File not found"
echo ""

# Test 5: Very low proportion to see more data retained
echo "TEST 5: Very low proportion (0.01) to retain more data"
echo "Command: Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.01"
Rscript minimum_proportion.R hypothetical_bug_counts.txt 0.01
echo "Expected output file: hypothetical_bug_counts_minProportion-0.01.txt"
echo "Check if file exists:"
ls -la hypothetical_bug_counts_minProportion-0.01.txt 2>/dev/null && echo "✓ File created" || echo "✗ File not found"
echo ""

# Test 6: Error handling - missing file
echo "TEST 6: Error handling - missing input file"
echo "Command: Rscript minimum_proportion.R nonexistent_file.txt"
Rscript minimum_proportion.R nonexistent_file.txt 2>&1 || echo "✓ Script handled missing file appropriately"
echo ""

# Test 7: Error handling - no arguments
echo "TEST 7: Error handling - no arguments provided"
echo "Command: Rscript minimum_proportion.R"
Rscript minimum_proportion.R 2>&1 || echo "✓ Script handled missing arguments appropriately"
echo ""

# Display sample of output files for verification
echo "========================================="
echo "SAMPLE OUTPUT VERIFICATION"
echo "========================================="

echo ""
echo "Sample from TEST 1 output (default 0.99):"
echo "First 5 rows and columns:"
if [ -f "hypothetical_bug_counts_minProportion-0.99.txt" ]; then
    head -6 hypothetical_bug_counts_minProportion-0.99.txt | cut -f1-6
else
    echo "Output file not found"
fi

echo ""
echo "Sample from TEST 2 output (0.5 threshold):"
echo "First 5 rows and columns:"
if [ -f "hypothetical_bug_counts_minProportion-0.5.txt" ]; then
    head -6 hypothetical_bug_counts_minProportion-0.5.txt | cut -f1-6
else
    echo "Output file not found"
fi

echo ""
echo "Sample from TEST 5 output (0.01 threshold - should retain more data):"
echo "First 5 rows and columns:"
if [ -f "hypothetical_bug_counts_minProportion-0.01.txt" ]; then
    head -6 hypothetical_bug_counts_minProportion-0.01.txt | cut -f1-6
else
    echo "Output file not found"
fi

echo ""
echo "========================================="
echo "All tests completed!"
echo "========================================="

echo ""
echo "Files created during testing:"
ls -la *minProportion*.txt custom_output.txt hypothetical_bug_counts.txt 2>/dev/null || echo "Some files may not have been created"

echo ""
echo "MANUAL VERIFICATION SUGGESTIONS:"
echo "1. Check that field_sample_01 has cockroach ~0.995 (9950/10000) - should be retained at 0.99+ threshold"
echo "2. Check that field_sample_02 has weevil ~0.9999 (9999/10000) - should be retained at 0.99+ threshold"
echo "3. Check that field_sample_04 (all zeros) has all NA values"
echo "4. Check that field_sample_07 (equal counts) has all NA values at high thresholds"
echo "5. Verify that taxa appearing in no retained samples are completely removed"
echo "6. Check rounding precision matches the input proportion precision"