import unittest

import ddt

from ._base import EvidenceCode


@ddt.ddt
class TestEvidenceCode(unittest.TestCase):

    @ddt.unpack
    @ddt.data(
        ['IEA'],
        ['TAS'],
        ['PCS'],
    )
    def test_parse_ok(self, code):
        ec: EvidenceCode = EvidenceCode.parse(code)
        self.assertEqual(ec, EvidenceCode[code])

    def test_parse_error(self):
        ec = EvidenceCode.parse('GIBBERISH')
        self.assertIsNone(ec)

