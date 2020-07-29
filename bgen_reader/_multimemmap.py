import numpy as np


class MultiMemMap:  # !!!should be record and offer order 'F' vs 'C'?

    _slot_dtype = "int32"

    _slots_length = 3

    def __init__(self, filename, mode, metameta_dtype="<U50"):
        # !!!cmk check all values of mode
        self._filename = filename
        self._mode = mode
        self._name_to_memmap = {}
        if filename.exists():
            self._offset = 0  # !!!cmk how come not using the inputted mode here?
            self._bootstrap = np.memmap(
                filename,
                dtype=self._slot_dtype,
                mode="r+",
                offset=self._offset,
                shape=(self._slots_length),
            )
            self._offset += self._bootstrap.size * self._bootstrap.itemsize
            assert self._slot_used <= self._slot_count

            self._metameta = np.memmap(
                filename,
                dtype=metameta_dtype,
                mode="r+",
                offset=self._offset,
                shape=(self._bootstrap[1], self._bootstrap[2]),
            )
            self._offset += self._metameta.size * self._metameta.itemsize

            try: #!!!cmk
                names = self._metameta[: self._slot_used, 0]
            except:
                print('!!!cmk')
            dtypes = self._metameta[: self._slot_used, 1]
            shapes = []
            for shape_as_str in self._metameta[: self._slot_used, 2]:
                shapes.append(
                    tuple([int(num_as_str) for num_as_str in shape_as_str.split(",")])
                )

            for slot_index in range(self._slot_used):
                memmap = np.memmap(
                    filename,
                    dtype=dtypes[slot_index],
                    mode="r+",
                    offset=self._offset,
                    shape=shapes[slot_index],
                )
                self._offset += memmap.size * memmap.itemsize
                self._name_to_memmap[names[slot_index]] = memmap
        else:
            assert mode == "w+", "MultiMemMap doesn't exist and mode isn't 'w+'"
            self._offset = 0
            self._bootstrap = np.memmap(
                self._filename,
                dtype=self._slot_dtype,
                mode="w+",
                offset=self._offset,
                shape=(self._slots_length),
            )
            self._offset += self._bootstrap.size * self._bootstrap.itemsize
            self._bootstrap[0] = 0
            self._bootstrap[1] = 20
            self._bootstrap[2] = 3
            self._bootstrap.flush() #!!!cmk offer (and use a global flush)

            self._metameta = np.memmap(
                self._filename,
                dtype=metameta_dtype,
                mode="r+",
                offset=self._offset,
                shape=(self._bootstrap[1], self._bootstrap[2]),
            )
            self._offset += self._metameta.size * self._metameta.itemsize

    @property
    def _slot_used(self):
        return self._bootstrap[0]

    @_slot_used.setter
    def _slot_used(self, value):
        self._bootstrap[0] = value

    @property
    def _slot_count(self):
        return int(self._bootstrap[1])

    @_slot_count.setter
    def _slot_count(self, value):
        self._bootstrap[1] = value

    @property
    def _metameta_count(self):
        return self._bootstrap[2]

    @_metameta_count.setter
    def _metameta_count(self, value):
        self._bootstrap[2] = value

    def __len__(self):
        return len(self._name_to_memmap)

    def __getitem__(self, name):
        return self._name_to_memmap[name]

    def append_empty(
        self, name, shape, dtype
    ):  # !!!cmk say that all these dtypes must be strings, not types
        assert self._mode == "w+", "Can only append with mode 'w+'"
        slot_index = len(self)
        self._metameta[slot_index, 0] = name
        self._metameta[slot_index, 1] = str(dtype)  # cmk repr???
        self._metameta[slot_index, 2] = str(shape)
        self._metameta.flush()
        memmap = np.memmap(
            self._filename, dtype=dtype, mode="r+", offset=self._offset, shape=shape
        )
        self._bootstrap[0] = (
            slot_index + 1
        )  # !!!cmk raise an error if every go over slots[2] e.g., 20
        self._bootstrap.flush()
        self._name_to_memmap[name] = memmap
        self._offset += memmap.size * memmap.itemsize
        memmap.flush()
        return memmap

    def popitem(
        self,
    ):  # As of Python 3.7 popitem remove the last item from a dictionary
        assert self._mode == "w+", "Can only append with mode 'w+'"
        slot_index = len(self) - 1
        name = self._metameta[slot_index, 0]
        self._metameta[slot_index, :] = ""
        self._metameta.flush()
        self._bootstrap[0] = slot_index
        self._bootstrap.flush()
        memmap = self._name_to_memmap.pop(name)
        self._offset -= memmap.size * memmap.itemsize
        memmap._mmap.close()

    def close(self):
        self.__exit__()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if (
            hasattr(self, "_name_to_memmap") and self._name_to_memmap is not None
        ):  # we need to test this because Python doesn't guarantee that __init__ was
            # fully run
            for memmap in self._name_to_memmap.values():
                memmap._mmap.close()
            self._name_to_memmap.clear()
            del (
                self._name_to_memmap
            )  # This allows __del__ and __exit__ to be called twice on the same object with
            # no bad effect.
        if (
            hasattr(self, "_bootstrap") and self._bootstrap is not None
        ):  # we need to test this because Python doesn't guarantee that __init__ was
            # fully run
            self._bootstrap._mmap.close()
            del (
                self._bootstrap
            )  # This allows __del__ and __exit__ to be called twice on the same object with
            # no bad effect.
        if (
            hasattr(self, "_metameta") and self._metameta is not None
        ):  # we need to test this because Python doesn't guarantee that __init__ was
            # fully run
            self._metameta._mmap.close()
            del (
                self._metameta
            )  # This allows __del__ and __exit__ to be called twice on the same object with
            # no bad effect
        if self._filename.stat().st_size > self._offset:
            with open(self._filename, "a") as fp:
                fp.truncate(self._offset)

    def __del__(self):
        self.__exit__()


# !!!cmk needs tests
