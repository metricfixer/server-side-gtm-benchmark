from __future__ import annotations

import csv
import json
import math
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from benchmark_core import VARIANTS, summarize  # noqa: E402


class DataIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=json.loads((ROOT/'data/raw/benchmark_raw.json').read_text(encoding='utf-8'))
        cls.summary=json.loads((ROOT/'data/processed/benchmark_summary.json').read_text(encoding='utf-8'))

    def test_row_and_variant_counts(self):
        self.assertEqual(len(self.raw),60)
        self.assertEqual(Counter(row['variant'] for row in self.raw),Counter({variant:15 for variant in VARIANTS}))

    def test_iterations_are_complete(self):
        for variant in VARIANTS:
            values=sorted(row['iteration'] for row in self.raw if row['variant']==variant)
            self.assertEqual(values,list(range(1,16)))

    def test_no_browser_or_request_errors(self):
        self.assertFalse(any(row['errors'] for row in self.raw))
        self.assertFalse(any(row['failed_request_count'] for row in self.raw))

    def test_summary_recalculates(self):
        recalculated=summarize(self.raw,runs_per_variant=15)
        self.assertEqual(recalculated,self.summary)

    def test_csv_matches_summary(self):
        
        with (ROOT/'data/processed/benchmark_medians.csv').open(encoding='utf-8',newline='') as handle:
            rows=list(csv.DictReader(handle))
        self.assertEqual(len(rows),11)
        mapping={'Browser requests':'request_count','Total transfer':'transfer_bytes','JavaScript requests':'js_request_count','JavaScript transfer':'js_transfer_bytes','Largest Contentful Paint':'lcp','Load event':'load','Long tasks':'longTaskCount','Long-task duration':'longTaskDuration','Total Blocking Time':'tbt','Browser event requests':'server_browser_event_requests','Logical destination deliveries':'logical_destination_deliveries'}
        for row in rows:
            field=mapping[row['metric']]
            for variant in VARIANTS:
                self.assertTrue(math.isclose(float(row[variant]),float(self.summary['variants'][variant][field]['median']),rel_tol=1e-12,abs_tol=1e-9))


if __name__=='__main__':
    unittest.main()
