import json
from pathlib import Path

from add_scripts.data import AddDatasetCode, load_new_records

OUTPUT_BASE = Path("next_release")

TABLE_1 = """| # | Title | Previous ID | Previous Edition | New ID | New Edition |
| - | ----- | ----------- | ---------------- | ------ | ----------- |
| C01 | High resolution vector polylines of the Antarctic coastline | 45c3cc90-098b-45e3-a809-16b80eed4ec2 | 7.9 | 3d32f755-67ea-4a9a-b925-93c0305b1ff8  | 7.10 |
| C02 | Medium resolution vector polylines of the Antarctic coastline | f2792d06-1e9d-4e00-a5c6-37d43bee5297 | 7.9 | c4a04761-311d-4031-89e9-00108f1b9c6a | 7.10 |
| C03 | High resolution vector polygons of the Antarctic coastline | 9b4fab56-4999-4fe1-b17f-1466e41151c4 | 7.9 | 2e3bf8c3-75b6-47cb-a8b3-e8dde9e4e8d4 | 7.10 |"""


def parse_markdown_table(table: str) -> list[dict]:
    lines = table.split('\n')
    headers = lines[0].split('|')
    headers = [h.strip() for h in headers if h.strip()]
    data = []
    for line in lines[2:]:
        row = line.split('|')
        row = [r.strip() for r in row if r.strip()]
        row = dict(zip(headers, row))
        data.append(row)
    return data


def parse_table1(table: str) -> list[dict]:
    table = parse_markdown_table(table)
    rows_ = []
    for row in table:
        row_ = {
            'code': AddDatasetCode[row['#']],
            'title': row['Title'],
            'previous_id': row['Previous ID'],
            'previous_edition': row['Previous Edition'],
            'new_id': row['New ID'],
            'new_edition': row['New Edition']
        }
        rows_.append(row_)
    return rows_


def set_record_id(record: dict, record_id: str) -> dict:
    record['file_identifier'] = record_id
    if 'identifiers' not in record['identification']:
        record['identification']['identifiers'] = []
    record['identification']['identifiers'].append(
        {
        "identifier": record_id,
        "href": f"https://data.bas.ac.uk/items/{record_id}",
        "namespace": "data.bas.ac.uk"
    })
    return record


def save_records(file_names: dict[AddDatasetCode, str], records: dict[AddDatasetCode, dict]) -> None:
    for record_code, record_data in records.items():
        file_name = file_names[record_code]
        record_id = record_data['file_identifier']
        record_path = OUTPUT_BASE / "records" / f"{file_name}-{record_id[:8]}.json"
        with record_path.open(mode="w") as f:
            json.dump(record_data, f, indent=2)


def process_resources(records: dict[AddDatasetCode, dict], datasets: list[dict]) -> dict[AddDatasetCode, dict]:
    for dataset in datasets:
        record = records[dataset['code']]
        records[dataset['code']] = set_record_id(record, dataset['new_id'])
    return records

def cleanup_original_records(file_names: dict[AddDatasetCode, str]) -> None:
    for record_code, file_name in file_names.items():
        record_path = OUTPUT_BASE / "records" / f"{file_name}.json"
        record_path.unlink()

def main() -> None:
    file_names, records = load_new_records()
    datasets = parse_table1(TABLE_1)
    records = process_resources(records, datasets)
    save_records(file_names, records)
    cleanup_original_records(file_names)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
