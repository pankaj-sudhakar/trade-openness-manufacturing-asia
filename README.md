# Replication package

This package supports **Trade Openness and Manufacturing Value Added Shares in South and Southeast Asia**. All estimates were rebuilt from official World Bank observations. No regression estimates were taken as input from the earlier manuscript.

## Data provenance

- Provider: World Bank, World Development Indicators, distributed by the official Data360 file service.
- Retrieval date: 1 October 2026, Asia/Calcutta.
- Eight original indicator CSVs are preserved in `raw/`; their file-service modification dates are 2–3 July 2026. File-service dates are not asserted to be country-series release dates.
- `data360_manifest.json` contains the full URLs, sizes, dates and SHA256 checksums.
- The conventional WDI API timed out. The official Data360 route succeeded; no unofficial data mirror was substituted.
- Data license: World Bank indicator pages identify CC BY 4.0. Retain attribution and provider metadata when sharing. See https://data.worldbank.org/indicator/NV.IND.MANF.ZS and https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets .

## Reproduce

Use Python 3.12 or a compatible version. Tested environment: NumPy 2.3.5, pandas 3.0.1, Matplotlib 3.10.3. From a terminal in this directory:

```text
python -m pip install -r requirements.txt
python analyze.py
python plot_figures.py
```

`analyze.py` is offline: it reads the archived CSVs, checks the panel, fits every model and saves outputs. It imports the included `linear_backend.py`, which implements OLS with a NumPy pseudoinverse, the explicit CR1 sandwich covariance and Student-t inference. SciPy and statsmodels are not required. Its incomplete-beta distribution calculations are checked against analytic Cauchy probabilities and standard t critical values.

`plot_figures.py` generates both manuscript figures from saved model output and fixed-composition regional means.

`download_data360.py` optionally obtains a NEW snapshot. Do not run it in the only copy of this archived package: it overwrites the raw indicator files and manifest. Use a separate directory/copy and retain this snapshot unchanged. A later release can legitimately change results.

## Files and main results

- `panel_all_countries.csv`: all 475 country-years, with missing data retained and correctly aligned lags/differences.
- `baseline_sample.csv`: 389 complete observations across 18 economies.
- `results/coverage.csv`: counts and incomplete years for all 19 economies in the initial frame.
- `results/nonmissing_by_indicator.csv`: indicator availability, including countries with no complete case.
- `results/models.json`: complete substantive coefficients, covariance-based SEs, intervals, p-values, sample sizes, cluster counts, rank, overall R-squared and partial R-squared for every specification.
- `results/*_sample.csv`: exact country-year identifiers for each model.
- `results/leave_one_out.csv`: each country-deletion estimate.
- `results/residual_*_correlations.csv`: descriptive serial and cross-country residual diagnostics.
- `results/audit.json`: sample checks and plotting-country composition.
- `results/environment.json`: library versions and indicator unit labels.
- `results/figure1.png`, `results/figure2.png`: regenerated figures; these do not reuse the original manuscript images.

The baseline trade slope is approximately 0.07269 (CR1 SE 0.01815). Its null-imposed wild-cluster bootstrap p-value is 0.0176. The annual-difference sample contains 369 valid consecutive-year pairs; previous-row differencing after complete-case deletion would incorrectly produce 371. On the 16-economy subsample, the valid difference sample is 349, not the earlier manuscript's 350.

Country-trend, annual-difference and restricted-sample findings are weaker than the earlier manuscript claimed. Do not restore significance claims from the original document.

## Inference details

- Economy-clustered CR1 factor: G/(G−1) × (N−1)/(N−K).
- Nominal intervals/p-values: Student t with G−1 degrees of freedom.
- Wild-cluster test: null imposed on the tested trade term; Rademacher signs at economy level; CR1 studentization; 4,999 simulations; seed 20261001; two-sided exceedance probability with a plus-one correction. Reported bars are nominal t intervals, not inverted bootstrap intervals.
- Time-aggregated HAC sensitivity: Bartlett kernel, two lags, T/(T−1) × (N−1)/(N−K), Student t with T−1 = 24 degrees of freedom.
- Partial R-squared: substantive regressors' contribution after projecting out included nuisance indicators and trends.
- India linear combination: the variance includes both variances and twice their covariance. Its single-economy identification prevents treating nominal intervals as reliable evidence of equality or difference.

## Implemented validation

Unique country/year/indicator records; annual frequency; positive income before logs; full grid size; full-rank design matrices; explicit self-merge verification of every annual difference; independent Frisch–Waugh–Lovell check of the baseline trade slope; agreement of bootstrap and main-estimator OLS/CR1 calculations; distribution checks; reproducible seeded simulations.

These checks establish computational consistency. They do not prove exogeneity, independence across countries, stationarity, causal identification or finite-sample coverage. The paper reports these limitations.

## Authorship and release

The author must inspect and understand the data, code and argument before submission. AI assistance with data acquisition, code, analysis and writing must be disclosed accurately under the chosen journal's policy. This is the data and code supplement for a manuscript under preparation, not a peer-reviewed publication. No DOI has been assigned. Cite the specific repository commit or release used for replication. No plagiarism or AI-detection certificate is included.

## Repository and citation

Public repository: https://github.com/pankaj-sudhakar/trade-openness-manufacturing-asia

Sudhakar, P. K. (2026). *Trade Openness and Manufacturing Value Added Shares in South and Southeast Asia: Data and Code* (Version 1.0.0) [Data set and computer software]. GitHub. Cite the specific commit used alongside this repository URL. The repository has no DOI.

The raw observations are attributed to the World Bank, World Development Indicators (via Data360), retrieved 1 October 2026. The source data retain their provider terms; repository publication does not replace those terms or imply World Bank endorsement. See the provenance manifest for exact source URLs and checksums.

`SHA256SUMS.txt` records the deposited file checksums (excluding this checksum file). On Windows PowerShell, use `Get-FileHash -Algorithm SHA256` to check an individual file. All Python analysis can run offline after the dependencies are installed.
