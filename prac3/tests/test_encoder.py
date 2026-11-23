"""Тесты машинного представления команд УВМ."""

import unittest

from src.encoder import decode_instruction, encode_instruction
from src.model import Instruction


class EncoderTest(unittest.TestCase):
    """Сравнение с байтами спецификации."""

    def test_encodes_load_constant(self) -> None:
        """Кодирование загрузки константы совпадает с заданием."""
        result = encode_instruction(Instruction("load_const", (541, 480)))
        self.assertEqual(result, bytes.fromhex("B2 43 00 0F 00 00 00"))

    def test_encodes_read(self) -> None:
        """Кодирование чтения совпадает с заданием."""
        result = encode_instruction(Instruction("read", (162, 986, 494)))
        self.assertEqual(result, bytes.fromhex("45 14 ED C1 3D 00 00"))

    def test_encodes_write(self) -> None:
        """Кодирование записи совпадает с заданием."""
        result = encode_instruction(Instruction("write", (894, 643, 71)))
        self.assertEqual(result, bytes.fromhex("CA 6F 18 14 8E 00 00"))

    def test_encodes_modulo(self) -> None:
        """Кодирование остатка совпадает с заданием."""
        result = encode_instruction(Instruction("mod", (860, 700, 606)))
        self.assertEqual(result, bytes.fromhex("81 6B E0 15 BC 04 00"))

    def test_decodes_encoded_instruction(self) -> None:
        """Декодирование восстанавливает исходную команду."""
        instruction = Instruction("write", (894, 643, 71))
        encoded = encode_instruction(instruction)
        self.assertEqual(decode_instruction(encoded), instruction)


if __name__ == "__main__":
    unittest.main()
