### What

GitHub provides a CSV file of the billing for Actions. However getting that into actionable data often requires a quick parse through for large organisations. You might want to answer questions quickly such:

* Which repository is spending the most money?
* Which builds are the slowest?
* Which builds are the most expensive?

Parsing this report can turn this into something actionable that your team can work on to reduce costs.

To get the report follow **Step 7** of [this page](https://docs.github.com/en/billing/managing-billing-for-github-actions/viewing-your-github-actions-usage#viewing-github-actions-usage-for-your-organization). Note that the billing rates for the [different SKUs are here](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions#per-minute-rates).

### Installation

* Requires Python 3
* Clone this repository or just grab `parse.py`

### Usage

```bash
python parse.py path-to-your-csv-file.csv --dump
```

Example:

```bash
python parse.py examples/384ddf93_2023-01-26_7.csv --dump

Report from 2023-01-20 to 2023-01-25


Owner                       |Number    |Minutes   |Cost      |Average   |Slowest
----------------------------|----------|----------|----------|----------|----------
andymckay                   |         5|        50|    0.4000|        10|        34
```

### Contributing

Pull requests always welcome. If you've got more complicated CSV files that could really test this library, those would be appreciated. But please ensure you've altered any organisation, repository or workflow names so that you don't accidentally leak any private information, no-one wants that.