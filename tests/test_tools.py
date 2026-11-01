import unittest
from debugging_eval.tools import get_error_summary,search_log,inspect_stack_trace,execute_tool
CASE={"case_id":"TEST-1","logs":"INFO service=api started\nERROR timeout waiting for upstream\n  at api.py:42\n"}
class ToolTests(unittest.TestCase):
    def test_error_summary(self):self.assertEqual(get_error_summary(CASE)["error_count"],1)
    def test_search(self):self.assertEqual(search_log(CASE,"TIMEOUT")["count"],1)
    def test_stack(self):self.assertEqual(inspect_stack_trace(CASE)["count"],1)
    def test_unknown_tool_rejected(self):self.assertIn("error",execute_tool("run_shell",{},CASE))
if __name__=="__main__":unittest.main()
