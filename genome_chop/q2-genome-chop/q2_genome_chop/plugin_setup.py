import importlib
from qiime2.plugin import Plugin, Str, Int, Bool, Choices, Citations
from q2_types.feature_data import FeatureData, Sequence
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    SequencesWithQuality, 
    SingleLanePerSampleSingleEndFastqDirFmt
)

from ._methods import chop_sequences
from ._types import ChoppedSequences

# Define citations
citations = Citations.load('citations.bib', package='q2_genome_chop')

# Create the plugin
plugin = Plugin(
    name='genome-chop',
    version='0.1.0',
    website='https://github.com/yourusername/q2-genome-chop',
    package='q2_genome_chop',
    description='A QIIME 2 plugin for chopping genome sequences into overlapping chunks',
    short_description='Chop genome sequences into overlapping chunks',
    citations=[citations['genome_chop_2025']]
)

# Register semantic types
plugin.register_semantic_types(ChoppedSequences)

# Register the method
plugin.methods.register_function(
    function=chop_sequences,
    inputs={
        'sequences': FeatureData[Sequence]
    },
    parameters={
        'chunk_size': Int,
        'slide_bp': Int,
        'max_sequences': Int,
        'random_seed': Int,
        'compress_output': Bool
    },
    outputs=[
        ('chopped_sequences', SampleData[SequencesWithQuality])
    ],
    input_descriptions={
        'sequences': 'Input DNA sequences in FASTA format to be chopped'
    },
    parameter_descriptions={
        'chunk_size': 'Size of each sequence chunk in base pairs',
        'slide_bp': 'Step size between chunks in base pairs. Use 0 for random mode',
        'max_sequences': 'Maximum number of output sequences to produce (optional)',
        'random_seed': 'Random seed for reproducible random mode (optional)',
        'compress_output': 'Whether to compress output files with gzip'
    },
    output_descriptions={
        'chopped_sequences': 'Chopped sequences in FASTQ format with quality scores'
    },
    name='Chop genome sequences',
    description='Chop genome sequences into overlapping chunks with sliding window or random sampling',
    citations=[citations['genome_chop_2025']]
)
