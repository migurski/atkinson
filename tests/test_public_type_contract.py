"""Prove declared C argument boundaries with the actual compiled extension."""
import unittest
from atkinson import atk


class Dimension:
    def __index__(self) -> int:
        return 1


class PublicTypeContract(unittest.TestCase):
    def test_integer_index_protocol_is_actually_supported(self) -> None:
        self.assertEqual(atk(Dimension(), Dimension(), b'\x80'), b'\xff')

    def test_keywords_are_rejected_by_the_genuine_positional_c_api(self) -> None:
        with self.assertRaises(TypeError):
            atk(w=1, h=1, pixels=b'\x00')

    def test_native_parser_rejects_unsupported_argument_types(self) -> None:
        for arguments in [('1', 1, b'\x00'), (1, '1', b'\x00'), (1.0, 1, b'\x00'), (1, 1.0, b'\x00'), (1, 1, '\x00'), (1, 1, None)]:
            with self.subTest(arguments=arguments), self.assertRaises(TypeError):
                atk(*arguments)
