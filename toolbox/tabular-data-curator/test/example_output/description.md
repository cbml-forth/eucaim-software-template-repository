# Notes on expected output determinism

Running the tool on `test/example_input/test.csv` with the default parameters
(`--outlier-method 1 --similarity-method 1 --imputation-method 1`) deterministically
reproduces the content of every generated report, with one exception:

* `test_results.json` contains a top-level `"timestamp"` field (ISO 8601, generation
  time) that differs on every run. All other fields are deterministic.
* Each `.xlsx` report embeds a document-creation timestamp in its internal
  `docProps/core.xml` metadata (written by `openpyxl`/`xlutils`), which differs on
  every run. The actual sheet contents (cell values, formatting, highlighted cells)
  are byte-identical across runs.

When validating integration, compare `test_results.json` ignoring the `timestamp`
field, and compare the `.xlsx` files by sheet content rather than by raw file bytes.
