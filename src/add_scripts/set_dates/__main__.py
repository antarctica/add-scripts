from typing import Dict
from pathlib import Path
from datetime import datetime, timezone

from add_scripts.utils import load_metadata_records, dump_metadata_records


metadata_records_path = Path(
    "/Users/felnne/OneDrive - NERC/Shared Documents/Projects/BAS Data Catalogue/Records/Datasets/add-7.6"
)


def set_dates(resource_config: Dict):
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)

    resource_config["metadata"]["date_stamp"] = now.date()
    resource_config["identification"]["dates"]["publication"]["date"] = now
    resource_config["identification"]["dates"]["released"]["date"] = now

    return resource_config


def main():
    records = load_metadata_records(records_path=metadata_records_path)

    for record_id, record_config in records.items():
        records[record_id] = set_dates(resource_config=record_config)

    dump_metadata_records(
        records_path=metadata_records_path,
        original_records_path=metadata_records_path,
        record_configs=list(records.values()),
    )


if __name__ == "__main__":
    main()
