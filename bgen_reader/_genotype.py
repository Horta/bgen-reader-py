from threading import RLock

import dask
import dask.bag
from cachetools import LRUCache, cached
from numpy import asarray, float64, full, nan
from tqdm import trange

from ._bgen_file import bgen_file
from ._bgen_metafile import bgen_metafile
from ._ffi import ffi, lib
from ._bgen_metafile import read_partition


def create_genotypes(bgen: bgen_file, metafile_filepath, verbose):
    nvariants = bgen.nvariants

    rg = _get_read_genotype(bgen, metafile_filepath)

    desc = "Mapping variants"
    return [
        rg(i, dask_key_name=str(i))
        for i in trange(nvariants, desc=desc, disable=not verbose)
    ]


def _get_read_genotype(bgen: bgen_file, metafile_filepath):
    from dask import delayed
    from dask.base import tokenize

    nsamples = bgen.nsamples
    nvariants = bgen.nvariants
    bgen_filepath = bgen.filepath

    with bgen_metafile(metafile_filepath) as mf:
        npartitions = mf.npartitions

    def read_genotype(i: int):

        part_size = _ceildiv(nvariants, npartitions)
        part = i // part_size
        j = i % part_size
        p = read_partition(metafile_filepath, part)
        nsub_parts = _estimate_best_nsub_parts(nsamples, part_size)
        spart_size = max(1, part_size // nsub_parts)
        sub_part = j // spart_size
        m = j % spart_size
        start = sub_part * spart_size
        end = min(len(p), (sub_part + 1) * spart_size)
        vaddrs = tuple(p.iloc[start:end]["vaddr"].tolist())
        g = read_genotype_partition(
            bgen_filepath, metafile_filepath, vaddrs, sub_part, spart_size
        )
        return g[m]

    name = "read_genotype-" + tokenize(bytes(metafile_filepath))
    return delayed(read_genotype, name, True, None, False)


cache = LRUCache(maxsize=3)
lock = RLock()


@cached(cache, lock=lock)
def read_genotype_partition(
    bgen_filepath, metafile_filepath, vaddrs, sub_part, spart_size
):
    genotypes = []
    for vaddr in vaddrs:
        with bgen_file(bgen_filepath) as bgen:
            nsamples = bgen.nsamples
            vg = lib.bgen_file_open_genotype(bgen._bgen_file, vaddr)
            if vg == ffi.NULL:
                raise RuntimeError(f"Could not open genotype (offset {vaddr})")
            ncombs = lib.bgen_genotype_ncombs(vg)
            p = full((nsamples, ncombs), nan, dtype=float64)
            lib.bgen_genotype_read(vg, ffi.cast("double *", p.ctypes.data))
            phased = bool(lib.bgen_genotype_phased(vg))
            ploidy = asarray(
                [lib.bgen_genotype_ploidy(vg, i) for i in range(nsamples)], int
            )
            missing = asarray(
                [lib.bgen_genotype_missing(vg, i) for i in range(nsamples)], bool
            )
            lib.bgen_genotype_close(vg)
            genotypes.append(
                {"probs": p, "phased": phased, "ploidy": ploidy, "missing": missing}
            )
    return genotypes


def _estimate_best_nsub_parts(nsamples, part_size):
    # Assume ideal block size, `bs`: 256KB
    # Assume 16 bytes per genotype per sample, `vs`
    # ideal nvariants to read: iv = bs / (vs * nsamples)
    # We then use iv to figure out in how many parts a partition will be subdivided
    # Let part_size be the number of variants in a partition
    # nsub_parts = min(int(part_size / iv), 1)
    bs = 256 * 1024
    vs = 16
    iv = bs / (vs * nsamples)
    return max(int(part_size / iv), 1)


def _ceildiv(a, b):
    return -(-a // b)
