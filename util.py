class LengthedGenerator(object):
    """Generator with an efficient, fixed length."""
    def __init__(self, gen, gen_len):
        self._gen = gen
        self._len = gen_len

    def __iter__(self):
        return iter(self._gen)

    def __len__(self):
        return self._len
