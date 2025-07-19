# QIIME 2 Plugin Installation Guide

## Package Structure

Create this directory structure:

```
q2-genome-chop/
├── setup.py
├── q2_genome_chop/
│   ├── __init__.py
│   ├── plugin_setup.py
│   ├── _methods.py
│   ├── _types.py
│   └── citations.bib
└── QIIME2_INSTALLATION.md
```

## Installation Steps

1. **Install QIIME 2 (if not already installed)**
   ```bash
   conda install -c qiime2 qiime2
   ```

2. **Activate your QIIME 2 environment**
   ```bash
   conda activate qiime2-2023.2  # or your QIIME 2 environment name
   ```

3. **Install the plugin in development mode**
   ```bash
   cd q2-genome-chop
   pip install -e .
   ```

4. **Refresh QIIME 2 plugin cache**
   ```bash
   qiime dev refresh-cache
   ```

5. **Verify installation**
   ```bash
   qiime genome-chop --help
   ```

## Usage Examples

### Basic Usage
```bash
# Import your FASTA sequences
qiime tools import \
  --input-path input_sequences.fasta \
  --output-path sequences.qza \
  --type 'FeatureData[Sequence]'

# Chop sequences with sliding window
qiime genome-chop chop-sequences \
  --i-sequences sequences.qza \
  --p-chunk-size 150 \
  --p-slide-bp 50 \
  --p-max-sequences 1000 \
  --o-chopped-sequences chopped_output.qza
```

### Random Mode
```bash
# Random sampling mode
qiime genome-chop chop-sequences \
  --i-sequences sequences.qza \
  --p-chunk-size 200 \
  --p-slide-bp 0 \
  --p-max-sequences 500 \
  --p-random-seed 42 \
  --o-chopped-sequences random_chunks.qza
```

### With Compression
```bash
# Compressed output
qiime genome-chop chop-sequences \
  --i-sequences sequences.qza \
  --p-chunk-size 100 \
  --p-slide-bp 25 \
  --p-compress-output \
  --o-chopped-sequences compressed_output.qza
```

### Export Results
```bash
# Export to view FASTQ files
qiime tools export \
  --input-path chopped_output.qza \
  --output-path exported_fastq/
```

## Parameters

- `--p-chunk-size`: Size of each sequence chunk in base pairs
- `--p-slide-bp`: Step size between chunks (use 0 for random mode)
- `--p-max-sequences`: Maximum number of output sequences (optional)
- `--p-random-seed`: Random seed for reproducible results (optional)
- `--p-compress-output`: Compress output files with gzip

## Key Differences from Standalone Script

1. **Input Format**: Uses QIIME 2 artifacts (.qza files) instead of raw FASTA
2. **Output Format**: Produces QIIME 2 artifacts that can be used in workflows
3. **Integration**: Works with other QIIME 2 tools and visualizations
4. **Reproducibility**: Built-in provenance tracking and random seed support
5. **Validation**: Automatic input/output validation through QIIME 2 framework

## Troubleshooting

- If `qiime genome-chop` doesn't appear, try `qiime dev refresh-cache`
- Check that you're in the correct conda environment
- Verify all dependencies are installed with `pip list | grep qiime2`
- For development, use `pip install -e .` to allow code changes without reinstalling
