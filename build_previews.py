"""Create small, lossless study-scope CSV views of the archived WDI files."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COUNTRIES = set('AFG BGD BTN IND MDV NPL PAK LKA BRN KHM IDN LAO MYS MMR PHL SGP THA TLS VNM'.split())
COLS = ['REF_AREA', 'REF_AREA_LABEL', 'TIME_PERIOD', 'OBS_VALUE', 'UNIT_MEASURE_LABEL', 'INDICATOR_LABEL']
REPO = 'https://github.com/pankaj-sudhakar/trade-openness-manufacturing-asia'
PIN = 'e32e2f833a3de8ee9e4952a9079949496a93d144'

def main():
    out = ROOT / 'study_data'
    out.mkdir(exist_ok=True)
    lines = ['# Open the study data', '',
        'GitHub cannot preview some large source CSVs. The files are intact and can be downloaded.', '',
        'These small extracts show available annual observations for the 19 economies in the initial study frame, 2000–2024. They retain source value strings without rounding. Blank values remain blank; absent source records are not filled in. These are not the complete-case regression sample.', '',
        '[Analysis panel: all 475 country-years](../panel_all_countries.csv) | [Baseline sample: 389 observations](../baseline_sample.csv)', '',
        '| Indicator | Preview study observations | Rows | Download original source CSV |',
        '|---|---|---:|---|']
    for item in json.loads((ROOT / 'data360_manifest.json').read_text()):
        source = ROOT / 'raw' / item['file']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256']
        with source.open(encoding='utf-8-sig', newline='') as f:
            rows = [r for r in csv.DictReader(f) if r['REF_AREA'] in COUNTRIES and r['FREQ'] == 'A' and 2000 <= int(r['TIME_PERIOD']) <= 2024]
        rows.sort(key=lambda r: (r['REF_AREA'], int(r['TIME_PERIOD'])))
        assert len({(r['REF_AREA'], r['TIME_PERIOD']) for r in rows}) == len(rows)
        target = out / item['file']
        with target.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
        with target.open(encoding='utf-8', newline='') as f:
            assert list(csv.DictReader(f)) == [{k:r[k] for k in COLS} for r in rows]
        assert target.stat().st_size < 100_000
        download = f'https://raw.githubusercontent.com/pankaj-sudhakar/trade-openness-manufacturing-asia/{PIN}/raw/{item["file"]}'
        lines.append(f'| {rows[0]["INDICATOR_LABEL"]} | [{item["indicator"]}]({item["file"]}) | {len(rows)} | [Full CSV]({download}) |')
    lines += ['', 'Source: World Bank, World Development Indicators via Data360, retrieved 1 October 2026. See [source URLs and checksums](../data360_manifest.json). Units are included in each extract.', '',
        'To open a full CSV: follow its download link, save the file, then use Excel Data > From Text/CSV (UTF-8, comma delimiter). A browser may display the raw text instead of downloading automatically; use Save As in that case.', '',
        'The analysis continues to use the unchanged original files in `raw/`. Rebuild these convenience views with `python build_previews.py`.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (ROOT / 'raw' / 'README.md').write_text('# Original World Bank source files\n\nThese full source CSVs may exceed GitHub\'s preview limit. Use the **[study-data index](../study_data/README.md)** for small viewable extracts and direct downloads of every original file. The source CSVs are unchanged.\n', encoding='utf-8')
    readme = ROOT / 'README.md'
    text = readme.read_text(encoding='utf-8-sig')
    section = '\n## Open or download the data\n\n- **[Browse small study-data tables](study_data/README.md)**: all eight indicators, with country, year, value and units.\n- **[Open the full analysis panel](panel_all_countries.csv)** or **[baseline estimation sample](baseline_sample.csv)**.\n- **[Download the complete repository ZIP](https://github.com/pankaj-sudhakar/trade-openness-manufacturing-asia/archive/refs/heads/main.zip)**, then extract it to open files locally.\n\nLarge CSVs in `raw/` exceed GitHub\'s preview limit. This is a display limitation, not file corruption. The study-data index includes direct downloads of the unchanged originals. Use the repository\'s `main` branch to see these navigation improvements; earlier commit links keep showing their original contents.\n\n'
    if '## Open or download the data' not in text:
        text = text.replace('## Data provenance', section + '## Data provenance')
        readme.write_text(text, encoding='utf-8')
    checks = []
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if not path.is_file() or '.git' in relative.parts or '__pycache__' in relative.parts or path.name == 'SHA256SUMS.txt':
            continue
        checks.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + relative.as_posix())
    (ROOT / 'SHA256SUMS.txt').write_text('\n'.join(checks) + '\n', encoding='utf-8')
    print(json.dumps({'previews': 8, 'source_checksums_verified': 8, 'preview_values_verified': True, 'largest_preview_bytes': max(p.stat().st_size for p in out.glob('*.csv'))}))

if __name__ == '__main__':
    main()
