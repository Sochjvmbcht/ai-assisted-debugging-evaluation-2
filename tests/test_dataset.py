import unittest
from debugging_eval.dataset import load_cases
class DatasetTests(unittest.TestCase):
    def test_balanced_dataset(self):
        cases=load_cases(); self.assertEqual(len(cases),15)
        counts={}
        for c in cases: counts[c["expected_root_cause"]]=counts.get(c["expected_root_cause"],0)+1
        self.assertEqual(set(counts.values()),{3})
if __name__=="__main__":unittest.main()
