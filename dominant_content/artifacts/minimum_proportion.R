#! Rscript
# Take a counts file and a proportion (default 0.99 for 99%)
# Report NA for any value that makes up less than that proportion of the sample count
# Then drop any taxa that are NA in all samples.
args = commandArgs(trailingOnly=TRUE)
if (length(args) < 1) stop("Need to supply a count table with samples as rows and taxa as columns.")
tableFile = args[1]
prop = 0.99
outputFile = NULL
if (length(args) > 1){
    prop = as.numeric(args[2])
    message("User specified proportion: ", prop)
}else{
    message("Using default proportion: ", prop)
}
if (length(args) > 2){
    outputFile = args[3]
    message("User specified output file: ", outputFile)
}
message("Only reporting taxa that account for at least ", prop * 100, "% of the counts for a given sample.")

# Read the count table
message("Reading count table from: ", tableFile)
counts <- read.table(tableFile, header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)

# Check if the table was read correctly
if (nrow(counts) == 0) stop("Count table is empty or could not be read properly.")
if (ncol(counts) == 0) stop("Count table has no taxa columns.")

message("Loaded table with ", nrow(counts), " samples and ", ncol(counts), " taxa.")

# Calculate row sums (total counts per sample)
row_sums <- rowSums(counts, na.rm = TRUE)

# Check for samples with zero counts
zero_count_samples <- which(row_sums == 0)
if (length(zero_count_samples) > 0) {
    message("Warning: Found ", length(zero_count_samples), " samples with zero total counts.")
    message("These samples will have all taxa set to NA.")
}

# Calculate number of decimal places in prop for rounding
prop_decimal_places <- nchar(sub(".*\\.", "", as.character(prop)))
if (!grepl("\\.", as.character(prop))) prop_decimal_places <- 0

# Apply proportion filter
# For each sample (row), set taxa to NA if they don't meet the proportion threshold
# and convert remaining values to proportions (0-1)
filtered_counts <- counts
for (i in 1:nrow(counts)) {
    if (row_sums[i] > 0) {
        # Calculate proportions for this sample
        sample_props <- counts[i, ] / row_sums[i]
        # Round proportions to match prop decimal places
        sample_props_rounded <- round(sample_props, prop_decimal_places)
        # Set values to NA if they don't meet the threshold, otherwise use rounded proportion
        filtered_counts[i, sample_props < prop] <- NA
        filtered_counts[i, sample_props >= prop] <- sample_props_rounded[sample_props >= prop]
    } else {
        # If sample has zero total counts, set all to NA
        filtered_counts[i, ] <- NA
    }
}

# Count how many values were set to NA
total_values <- nrow(counts) * ncol(counts)
na_values <- sum(is.na(filtered_counts))
message("Set ", na_values, " out of ", total_values, " values to NA (", 
        round(na_values/total_values * 100, 2), "%).")

# Remove taxa that are NA in all samples
taxa_all_na <- colSums(is.na(filtered_counts)) == nrow(filtered_counts)
filtered_counts <- filtered_counts[, !taxa_all_na]

n_removed_taxa <- sum(taxa_all_na)
message("Removed ", n_removed_taxa, " taxa that were NA in all samples.")
message("Final table has ", nrow(filtered_counts), " samples and ", ncol(filtered_counts), " taxa.")

# Generate output filename
if (is.null(outputFile)) {
    # Extract base name and extension
    base_name <- sub("\\.[^.]*$", "", basename(tableFile))
    extension <- sub(".*\\.", "", basename(tableFile))
    if (base_name == basename(tableFile)) {
        # No extension found
        extension <- ""
        base_name <- basename(tableFile)
    }
    
    # Create output filename with proportion inserted
    if (extension == "") {
        output_file <- paste0(base_name, "_minProportion-", prop)
    } else {
        output_file <- paste0(base_name, "_minProportion-", prop, ".", extension)
    }
} else {
    output_file <- outputFile
}

# Write the filtered table
write.table(filtered_counts, file = output_file, sep = "\t", quote = FALSE, 
            row.names = TRUE, col.names = NA)

message("Filtered proportion table written to: ", output_file)