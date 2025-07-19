from setuptools import setup, find_packages

setup(
    name="q2-genome-chop",
    version="0.1.0",
    description="QIIME 2 plugin for chopping genome sequences into overlapping chunks",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/q2-genome-chop",
    packages=find_packages(),
    package_data={
        'q2_genome_chop': ['citations.bib'],
    },
    entry_points={
        'qiime2.plugins': ['q2-genome-chop=q2_genome_chop.plugin_setup:plugin']
    },
    install_requires=[
        'qiime2 >= 2023.2.0',
        'scikit-bio',
        'pandas',
        'numpy'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)
