from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def assert_valid(self,instance_path,schema_path):
        instance=json.loads((ROOT/instance_path).read_text(encoding='utf-8'))
        schema=json.loads((ROOT/schema_path).read_text(encoding='utf-8'))
        errors=sorted(Draft202012Validator(schema,format_checker=FormatChecker()).iter_errors(instance),key=lambda e:list(e.path))
        self.assertEqual(errors,[],"\n".join(f"{list(e.path)}: {e.message}" for e in errors))

    def test_raw(self):
        self.assert_valid('data/raw/benchmark_raw.json','data/schema/benchmark-raw.schema.json')

    def test_summary(self):
        self.assert_valid('data/processed/benchmark_summary.json','data/schema/benchmark-summary.schema.json')

    def test_manifest(self):
        self.assert_valid('data/manifest/benchmark-manifest.json','data/schema/benchmark-manifest.schema.json')

    def test_article_reference(self):
        self.assert_valid('article-reference.json','data/schema/article-reference.schema.json')


if __name__=='__main__':
    unittest.main()
