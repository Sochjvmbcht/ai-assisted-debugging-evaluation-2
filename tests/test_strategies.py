import unittest
from debugging_eval.strategies import RuleBasedStrategy
class RuleStrategyTests(unittest.TestCase):
    def test_each_label(self):
        samples={"DATABASE_CONNECTION_POOL_EXHAUSTED":"ERROR connection pool exhausted db_pool active=20 max=20","NETWORK_TIMEOUT":"ERROR ReadTimeout upstream request timed out","NULL_REFERENCE":"ERROR AttributeError NoneType object has no attribute id","OUT_OF_MEMORY":"FATAL OOMKilled MemoryError heap space","AUTHENTICATION_FAILURE":"ERROR HTTP status=401 expired access token"}
        strategy=RuleBasedStrategy()
        for expected,logs in samples.items():
            with self.subTest(expected=expected):
                result,_=strategy.diagnose({"logs":logs});self.assertEqual(result["root_cause"],expected)
if __name__=="__main__":unittest.main()
