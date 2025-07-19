#!/usr/bin/env Rscript
# Split a counts table into two tables:
# 1. Unclassified genera (columns starting with "Unclassified")
# 2. Species (all other columns)

args = commandArgs(trailingOnly=TRUE)
if (length(args) < 1) stop("Need to supply a count table with samples as rows and taxa as columns.")

tableFile = args[1]
message("Reading count table from: ", tableFile)

# Read the count table
counts <- read.table(tableFile, header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)

# Check if the table was read correctly
if (nrow(counts) == 0) stop("Count table is empty or could not be read properly.")
if (ncol(counts) == 0) stop("Count table has no taxa columns.")

message("Loaded table with ", nrow(counts), " samples and ", ncol(counts), " taxa.")

# Identify columns that start with "Unclassified"
unclassified_cols <- grepl("^Unclassified", colnames(counts))
unclassified_count <- sum(unclassified_cols)
species_count <- sum(!unclassified_cols)

message("Found ", unclassified_count, " unclassified genera and ", species_count, " species columns.")

# Create the two tables
unclassified_table <- counts[, unclassified_cols, drop = FALSE]
species_table <- counts[, !unclassified_cols, drop = FALSE]

# Generate output filenames
base_name <- sub("\\.[^.]*$", "", basename(tableFile))
extension <- sub(".*\\.", "", basename(tableFile))
if (base_name == basename(tableFile)) {
    # No extension found
    extension <- "tsv"
    base_name <- basename(tableFile)
}

unclassified_file <- paste0(base_name, "_unclassifiedGenus.", extension)
species_file <- paste0(base_name, "_species.", extension)

# Write the tables
write.table(unclassified_table, file = unclassified_file, sep = "\t", quote = FALSE, 
            row.names = TRUE, col.names = NA)
write.table(species_table, file = species_file, sep = "\t", quote = FALSE, 
            row.names = TRUE, col.names = NA)

message("Unclassified genera table written to: ", unclassified_file)
message("Species table written to: ", species_file)
message("Both tables contain all ", nrow(counts), " samples.")