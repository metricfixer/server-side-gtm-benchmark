from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]


class RepositoryMetadataTests(unittest.TestCase):
    def test_urls_are_consistent(self):
        config=json.loads((ROOT/'config/repository.json').read_text(encoding='utf-8'))
        for relative in ['README.md','ARTICLE_REFERENCE.md','CITATION.cff','article-reference.json']:
            text=(ROOT/relative).read_text(encoding='utf-8')
            self.assertIn(config['article_url'],text)
            self.assertIn(config['repository_url'],text)
        snippet=(ROOT/'snippets/article-repository-block.html').read_text(encoding='utf-8')
        self.assertIn(config['repository_url'],snippet)
        self.assertIn(config['release_url'],snippet)

    def test_repository_yaml_parses(self):
        data=yaml.safe_load((ROOT/'REPOSITORY_METADATA.yml').read_text(encoding='utf-8'))
        self.assertEqual(data['repository']['name'],'server-side-gtm-benchmark')

    def test_runner_help(self):
        result=subprocess.run([sys.executable,str(ROOT/'src/run_benchmark.py'),'--help'],capture_output=True,text=True,check=True)
        self.assertIn('--runs-per-variant',result.stdout)
        self.assertIn('--browser-executable',result.stdout)


if __name__=='__main__':
    unittest.main()
