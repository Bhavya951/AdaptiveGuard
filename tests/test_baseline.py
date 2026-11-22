import unittest
from src.baseline import predict, metrics, run

class TestBaseline(unittest.TestCase):
    def test_predict(self):
        self.assertEqual(predict("override-demo-rule"),1)
        self.assertEqual(predict("ordinary prompt"),0)
    def test_metrics(self):
        self.assertEqual(metrics([1,0],[1,0])["f1"],1.0)
        self.assertEqual(metrics([0,0],[1,0])["fp"],1)
    def test_invalid(self):
        with self.assertRaises(ValueError): metrics([],[])
    def test_run(self):
        self.assertEqual(run()["tp"],2)

if __name__ == "__main__": unittest.main()
