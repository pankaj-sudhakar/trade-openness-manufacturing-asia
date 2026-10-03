# Open the study data

GitHub cannot preview some large source CSVs. The files are intact and can be downloaded.

These small extracts show available annual observations for the 19 economies in the initial study frame, 2000–2024. They retain source value strings without rounding. Blank values remain blank; absent source records are not filled in. These are not the complete-case regression sample.

[Analysis panel: all 475 country-years](../panel_all_countries.csv) | [Baseline sample: 389 observations](../baseline_sample.csv)

| Indicator | Preview study observations | Rows | Download original source CSV |
|---|---|---:|---|
| Manufacturing, value added (% of GDP) | [NV.IND.MANF.ZS](NV.IND.MANF.ZS.csv) | 455 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NV.IND.MANF.ZS.csv) |
| Trade (% of GDP) | [NE.TRD.GNFS.ZS](NE.TRD.GNFS.ZS.csv) | 403 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NE.TRD.GNFS.ZS.csv) |
| Foreign direct investment, net inflows (% of GDP) | [BX.KLT.DINV.WD.GD.ZS](BX.KLT.DINV.WD.GD.ZS.csv) | 466 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/BX.KLT.DINV.WD.GD.ZS.csv) |
| Gross capital formation (% of GDP) | [NE.GDI.TOTL.ZS](NE.GDI.TOTL.ZS.csv) | 403 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NE.GDI.TOTL.ZS.csv) |
| GDP per capita (constant 2015 US$) | [NY.GDP.PCAP.KD](NY.GDP.PCAP.KD.csv) | 475 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NY.GDP.PCAP.KD.csv) |
| Manufacturing, value added (annual % growth) | [NV.IND.MANF.KD.ZG](NV.IND.MANF.KD.ZG.csv) | 458 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NV.IND.MANF.KD.ZG.csv) |
| Exports of goods and services (% of GDP) | [NE.EXP.GNFS.ZS](NE.EXP.GNFS.ZS.csv) | 403 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NE.EXP.GNFS.ZS.csv) |
| Imports of goods and services (% of GDP) | [NE.IMP.GNFS.ZS](NE.IMP.GNFS.ZS.csv) | 403 | [Full CSV](https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/e32e2f833a3de8ee9e4952a9079949496a93d144/raw/NE.IMP.GNFS.ZS.csv) |

Source: World Bank, World Development Indicators via Data360, retrieved 1 October 2026. See [source URLs and checksums](../data360_manifest.json). Units are included in each extract.

To open a full CSV: follow its download link, save the file, then use Excel Data > From Text/CSV (UTF-8, comma delimiter). A browser may display the raw text instead of downloading automatically; use Save As in that case.

The analysis continues to use the unchanged original files in `raw/`. Rebuild these convenience views with `python build_previews.py`.
