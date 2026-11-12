"""Exercise the genuine positional C API and its integer index conversion."""
from atkinson import atk


class Dimension:
    def __index__(self) -> int:
        return 1


first: bytes = atk(1, 1, b'\x7f')
indexed: bytes = atk(Dimension(), Dimension(), b'\x80')
empty: bytes = atk(0, 0, b'')
assert first == b'\x00'
assert indexed == b'\xff'
assert empty == b''
