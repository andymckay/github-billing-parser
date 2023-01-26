import parse
import unittest
import datetime
import decimal


class TestVerify(unittest.TestCase):
    def test_verify(self):
        parse.verify("examples/384ddf93_2023-01-26_7.csv")
        for filename in ["examples/does-not-exist.csv", "examples/does-not-exist.json"]:
            with self.assertRaises(AssertionError):
                parse.verify(filename)


class TestParse(unittest.TestCase):
    def test_parse_bad_product(self):
        report = parse.Report()
        with self.assertRaises(AssertionError):
            report.parse("examples/bad-product.csv")

    def test_parse_actions(self):
        report = parse.Report()
        report.parse("examples/384ddf93_2023-01-26_7.csv")
        runs = report.actions.runs
        self.assertEqual(3, len(runs.keys()))
        run = runs[".github/workflows/blank.yml"][0]

        self.assertEqual(run["quantity"], 34)
        for key in ["multiplier", "price"]:
            self.assertIsInstance(run[key], decimal.Decimal)

        self.assertIsInstance(run["date"], datetime.date)

    def test_parse_counts(self):
        report = parse.Report()
        report.parse("examples/384ddf93_2023-01-26_7.csv")
        actions = report.actions
        self.assertEqual(actions.workflows[".github/workflows/blank.yml"]["number"], 2)
        self.assertEqual(actions.repos["playground"]["number"], 2)
        self.assertEqual(actions.owners["andymckay"]["number"], 5)


if __name__ == "__main__":
    unittest.main()
