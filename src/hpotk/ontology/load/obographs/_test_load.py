import json
import unittest

from ._load import extract_ontology_version


class TestLoad(unittest.TestCase):

    def test_parse_ontology_version(self):
        meta = """
        {
          "version": "http://purl.obolibrary.org/obo/hp/releases/2022-10-05/hp.json"
        }
        """
        meta = json.loads(meta)
        version = extract_ontology_version(meta)
        self.assertEqual(version, '2022-10-05')

    def test_parse_ontology_version_from_bpv(self):
        meta = """
        {
          "basicPropertyValues": [
            {
              "pred": "http://www.w3.org/2002/07/owl#versionInfo",
              "val": "2022-10-05"
            }
          ]
        }
        """
        meta = json.loads(meta)
        version = extract_ontology_version(meta)
        self.assertEqual(version, '2022-10-05')
