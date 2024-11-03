import json
from pathlib import Path
from typing import Dict, List, Optional

from bas_metadata_library.standards.iso_19115_2 import MetadataRecordConfigV3


def workaround_unset_dates(record_path: Path):
    with open(record_path, mode="r") as record_file:
        record_config = json.load(record_file)
        if record_config["identification"]["dates"]["publication"] == "":
            record_config["identification"]["dates"]["publication"] = "2000-01-01"
        if record_config["identification"]["dates"]["released"] == "":
            record_config["identification"]["dates"]["released"] = "2000-01-01"
    with open(record_path, mode="w") as record_file:
        json.dump(record_config, record_file, indent=2)


def load_metadata_records(records_path: Path) -> Dict[str, dict]:
    records: Dict[str, dict] = {}

    for record_path in records_path.glob("*.json"):
        # workaround for unset dates
        workaround_unset_dates(record_path=record_path)

        record_config = MetadataRecordConfigV3()
        record_config.load(file=record_path)
        records[record_config.config["file_identifier"]] = record_config.config

    return records


def get_file_name_for_record(
    original_file_names: List[Path], record_id: str
) -> Optional[str]:
    for original_file_name in original_file_names:
        if record_id[:8] in original_file_name.name:
            return str(original_file_name.name)

    return None


def dump_metadata_records(
    records_path: Path, original_records_path: Path, record_configs: List[dict]
):
    # ensure output directory exists
    records_path.resolve().mkdir(parents=True, exist_ok=True)

    # get original file names
    original_file_names = list(original_records_path.glob("*.json"))

    for record_config in record_configs:
        record_name = get_file_name_for_record(
            original_file_names=original_file_names,
            record_id=record_config["file_identifier"],
        )
        if record_name is None:
            print(
                f"Cannot find original file name for record ID: {record_config['file_identifier']}"
            )
            continue

        record_path = records_path.joinpath(record_name)
        record_configuration = MetadataRecordConfigV3(**record_config)
        record_configuration.dump(file=record_path)

        # fix formatting of record
        with open(record_path, mode="r") as record_file:
            record_config = json.load(record_file)
        with open(record_path, mode="w") as record_file:
            json.dump(record_config, record_file, indent=2)
