"""The declared API must reject unsupported inputs and keyword arguments."""
from atkinson import atk

atk('1', 1, b'\x00')  # EXPECT_ERROR
atk(1, '1', b'\x00')  # EXPECT_ERROR
atk(1.0, 1, b'\x00')  # EXPECT_ERROR
atk(1, 1.0, b'\x00')  # EXPECT_ERROR
atk(1, 1, '\x00')  # EXPECT_ERROR
atk(1, 1, None)  # EXPECT_ERROR
atk(w=1, h=1, pixels=b'\x00')  # EXPECT_ERROR
wrong: str = atk(1, 1, b'\x00')  # EXPECT_ERROR
