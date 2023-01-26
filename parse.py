import argparse
import copy
import csv
import datetime
from decimal import Decimal
import os
import sys


def verify(filename):
    filename = os.path.expanduser(filename)
    assert os.path.exists(filename), f"Cannot access the file: {filename}."
    assert filename.endswith(".csv"), f"File must be a CSV file: {filename}."


class Report:
    def __init__(self):
        self.actions = Actions()
        self.shared_storage = SharedStorage()
        self.products = {
            Actions.name: self.actions,
            SharedStorage.name: self.shared_storage,
        }

    def parse(self, filename):
        with open(filename, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product = self.products.get(row["Product"])
                assert product, f"Unknown product: {row['Product']}"
                product.parse_row(row)

        for product in self.products.values():
            product.generate_summaries()

    def dump(self):
        for product in self.products.values():
            product.dump()


class Actions(Report):
    name = "Actions"

    def __init__(self):  # pylint: disable=super-init-not-called
        self.owners = {}
        self.repos = {}
        self.workflows = {}
        self.runs = {}
        self._longest = {
            "workflow_name": 0,
            "repo_name": 0,
            "owner_name": 0,
        }
        self.dates = {"start": datetime.date.max, "end": datetime.date.min}

    def parse_row(self, row):
        self.runs.setdefault(row["Actions Workflow"], [])
        date = datetime.date(*[int(x) for x in row["Date"].split("-")])
        self.runs[row["Actions Workflow"]].append(
            {
                "quantity": int(row["Quantity"]),
                "type": row["Unit Type"],
                "multiplier": Decimal(row["Multiplier"]),
                "price": Decimal(row["Price Per Unit ($)"]),
                "owner": row["Owner"],
                "repository": row["Repository Slug"],
                "date": date,
                "cost": Decimal(row["Price Per Unit ($)"])
                * Decimal(row["Multiplier"])
                * int(row["Quantity"]),
                "sku": row["SKU"],
            }
        )
        # Set the longest names.
        self._longest["workflow_name"] = max(
            self._longest["workflow_name"], len(row["Actions Workflow"])
        )
        self._longest["repo_name"] = max(
            self._longest["repo_name"], len(row["Repository Slug"])
        )
        self._longest["owner_name"] = max(
            self._longest["owner_name"], len(row["Owner"])
        )

        self.dates["start"] = min(self.dates["start"], date)
        self.dates["end"] = max(self.dates["end"], date)

    def generate_summaries(self):
        default = {
            "number": 0,
            "slowest": 0,
            "average": 0,
        }
        for key, value in self.runs.items():
            self.workflows.setdefault(key, copy.copy(default))
            for run in value:
                self.owners.setdefault(run["owner"], copy.copy(default))
                self.repos.setdefault(run["repository"], copy.copy(default))
                self.owners[run["owner"]]["number"] += 1
                self.repos[run["repository"]]["number"] += 1

                workflow = self.workflows[key]

                workflow["number"] += 1
                workflow["slowest"] = max(workflow["slowest"], run["quantity"])
                workflow["minutes"] = workflow.get("minutes", 0) + run["quantity"]
                workflow["average"] = Decimal(workflow["minutes"] / workflow["number"])
                workflow["cost"] = workflow.get("cost", 0) + run["cost"]

                repo = self.repos[run["repository"]]
                repo["slowest"] = max(repo["slowest"], run["quantity"])
                repo["minutes"] = repo.get("minutes", 0) + run["quantity"]
                repo["average"] = Decimal(repo["minutes"] / repo["number"])
                repo["cost"] = repo.get("cost", 0) + run["cost"]

                owner = self.owners[run["owner"]]
                owner["slowest"] = max(owner["slowest"], run["quantity"])
                owner["minutes"] = owner.get("minutes", 0) + run["quantity"]
                owner["average"] = Decimal(owner["minutes"] / owner["number"])
                owner["cost"] = owner.get("cost", 0) + run["cost"]

    def dump(self):
        biggest = max(self._longest.values())

        def newline():
            print("\n")

        def dump_header(first):
            header = f"{first}|{'Number':10}|{'Minutes':10}|{'Cost':10}"
            header += f"|{'Average':10}|{'Slowest':10}"
            columns = header.split("|")
            print(header)
            print("|".join(f"{'-'*len(c)}" for c in columns))

        def dump_rows(rows):
            for key, values in rows.items():
                row = f"{key:<{biggest}}"
                row += (
                    f"|{values['number']:10}|{values['minutes']:10}|{values['cost']:10}"
                )
                row += f"|{values['average']:10}|{values['slowest']:10}"
                print(row)
            newline()

        def dump_run_headers(first):
            header = f"{first}|{'Minutes':10}|{'Cost':10}"
            columns = header.split("|")
            print(header)
            print("|".join(f"{'-'*len(c)}" for c in columns))

        def dump_runs(runs):
            for run in runs:
                date = str(run["date"])
                row = f"{date:<{biggest}}"
                row += f"|{run['quantity']:10}|{run['cost']:10}"
                print(row)
            newline()

        print(f"Report from {self.dates['start']} to {self.dates['end']}")
        newline()

        dump_header(f"{'Owner':<{biggest}}")
        dump_rows(self.owners)

        dump_header(f"{'Repository':<{biggest}}")
        dump_rows(self.repos)

        dump_header(f"{'Workflow':<{biggest}}")
        dump_rows(self.workflows)

        for k, runs in self.runs.items():
            dump_run_headers(f"{k:<{biggest}}")
            dump_runs(runs)


class SharedStorage(Report):
    name = "Shared Storage"

    def __init__(self):  # pylint: disable=super-init-not-called
        pass

    def parse_row(self, row):
        # Not parsing shared storage at this moment.
        pass

    def generate_summaries(self):
        # Not generating totals for shared storage at this moment.
        pass

    def dump(self):
        # Not dumping for shared storage at this moment.
        pass


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Billing file to parse")
    parser.add_argument("--dump", help="Dump the parsed data", action="store_true")
    parsed = parser.parse_args(args)

    verify(parsed.filename)
    report = Report()
    report.parse(parsed.filename)

    if parsed.dump:
        report.dump()


if __name__ == "__main__":
    main(sys.argv[1:])
