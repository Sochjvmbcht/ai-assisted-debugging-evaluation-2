import unittest
from debugging_eval.evaluator import score_diagnosis, summarize
class EvaluatorTests(unittest.TestCase):
    def test_correct_complete(self):
        d={"root_cause":"NETWORK_TIMEOUT","explanation":"Upstream read timed out.","recommended_actions":["Check upstream."]}
        s=score_diagnosis(d,"NETWORK_TIMEOUT");self.assertTrue(s["correct"]);self.assertTrue(s["complete"])
    def test_unknown_not_complete(self):
        s=score_diagnosis({"root_cause":"UNKNOWN","explanation":"No evidence","recommended_actions":[]},"NETWORK_TIMEOUT")
        self.assertFalse(s["correct"]);self.assertFalse(s["complete"])
    def test_summary_has_latency_percentiles_and_failures(self):
        report={"results":[{"strategy":"x","latency_ms":10,"correct":True,"complete":True,"estimated_tokens":5,"tool_calls":1,"parse_error":False,"error":None},{"strategy":"x","latency_ms":30,"correct":False,"complete":False,"estimated_tokens":7,"tool_calls":0,"parse_error":True,"error":"timeout"}]}
        s=summarize(report)[0];self.assertEqual(s["median_latency_ms"],20);self.assertEqual(s["failures"],1)
if __name__=="__main__":unittest.main()
