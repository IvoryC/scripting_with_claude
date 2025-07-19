#!/usr/bin/env Rscript
# Sort tab-delimited file by adding a count column, sorting rows hierarchically,
# and sorting taxa columns by frequency.

# Function to sort TSV file
sort_tsv_file <- function(input_file) {
  
  # Check if file exists
  if (!file.exists(input_file)) {
    stop(paste("Error: File", input_file, "not found."))
  }
  
  tryCatch({
    # Read the tab-delimited file
    df <- read.table(input_file, sep = "\t", header = TRUE, row.names = 1, 
                     check.names = FALSE, stringsAsFactors = FALSE)
    
    # Sort taxa (columns) by frequency - most represented taxa first
    taxa_counts <- sapply(df, function(col) {
      sum(!is.na(col) & col != 0)
    })
    sorted_taxa <- names(sort(taxa_counts, decreasing = TRUE))
    df <- df[, sorted_taxa, drop = FALSE]
    
    # Count non-zero/non-null values in each row (excluding NA values)
    count_col <- apply(df, 1, function(row) {
      sum(!is.na(row) & row != 0)
    })
    
    # Add count column as the first column
    df <- cbind(count = count_col, df)
    
    # Sort by all columns in order (count first, then original columns)
    df_sorted <- df[do.call(order, df), , drop = FALSE]
    
    # Generate output filename
    base_name <- tools::file_path_sans_ext(input_file)
    extension <- tools::file_ext(input_file)
    output_file <- paste0(base_name, "_sorted.", extension)
    
    # Write sorted data to output file
    write.table(df_sorted, file = output_file, sep = "\t", quote = FALSE, 
                row.names = TRUE, col.names = NA)
    
    cat("Sorted file saved as:", output_file, "\n")
    cat("Added count column and sorted", nrow(df_sorted), "rows\n")
    cat("Sorted", length(sorted_taxa), "taxa by frequency (most common first)\n")
    
  }, error = function(e) {
    stop(paste("Error processing file:", e$message))
  })
}

# Main function to handle command line arguments
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) != 1) {
    cat("Usage: Rscript sort_tsv.R <input_file>\n")
    cat("Example: Rscript sort_tsv.R data.tsv\n")
    quit(status = 1)
  }
  
  input_file <- args[1]
  sort_tsv_file(input_file)
}

# Run main function if script is executed directly
if (!interactive()) {
  main()
}
