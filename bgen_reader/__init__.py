"""
BGEN file format reader
=======================

`BGEN <http://www.well.ox.ac.uk/~gav/bgen_format/>`_ is a file format for storing large
genetic datasets. It supports both unphased genotypes and phased haplotype data with
variable ploidy and number of alleles. It was designed to provides a compact data
representation without sacrificing variant access performance.

Functions
---------
allele_expectation  Compute the expectation of each allele.
allele_frequency    Compute allele frequency from its expectation.
compute_dosage      Compute dosage from allele expectation.
create_metafile     Create metafile.
download            Download a file from a given url.
example_files       Create a temporary folder with the given files.
read_bgen           Read a given BGEN file.
test                Verify this package's integrity.

Documentation can be found at <https://github.com/limix/bgen-reader-py>.
"""
from ._dosage import allele_expectation, allele_frequency, compute_dosage
from ._download import download
from ._example import example_files
from ._file import BGEN_CACHE_HOME
from ._metadata import create_metafile
from ._reader import read_bgen
from ._testit import test

try:
    from ._ffi import ffi

    del ffi
except Exception as e:
    _ffi_err = """
It is likely caused by a broken installation of this package.
Please, make sure you have a C compiler and try to uninstall
and reinstall the package again."""

    raise RuntimeError(str(e) + _ffi_err)

__version__ = "4.0.0"

__all__ = [
    "BGEN_CACHE_HOME",
    "__version__",
    "allele_expectation",
    "allele_frequency",
    "compute_dosage",
    "create_metafile",
    "download",
    "example_files",
    "read_bgen",
    "test",
]
