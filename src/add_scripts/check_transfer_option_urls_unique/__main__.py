from typing import Dict, List
from pathlib import Path

from add_scripts.utils import load_metadata_records


lookup_items_path = Path("./lookup_items.json")

metadata_records_path = Path(
    "/Users/felnne/OneDrive - NERC/Shared Documents/Projects/BAS Data Catalogue/Records/Datasets/add-7.6"
)


def get_transfer_option_urls(record_config: dict) -> Dict[str, str]:
    transfer_option_urls: Dict[str, str] = {}

    for distribution in record_config["distribution"]:
        if "href" not in distribution["format"]:
            continue

        if (
            distribution["transfer_option"]["online_resource"]["href"]
            == "https://data.bas.ac.uk/download/"
        ):
            print(
                f"Record ID [{record_config['file_identifier']}] has a transfer option without an artefact ID"
            )

        transfer_option_urls[distribution["format"]["href"]] = distribution[
            "transfer_option"
        ]["online_resource"]["href"]

    return transfer_option_urls


def list_non_unique_transfer_option_urls(
    transfer_urls_by_record: Dict[str, Dict[str, str]],
) -> None:
    for source_record_id, source_transfer_urls in transfer_urls_by_record.items():
        for source_media_type, source_transfer_url in source_transfer_urls.items():
            for (
                compare_record_id,
                compare_transfer_urls,
            ) in transfer_urls_by_record.items():
                for (
                    compare_media_type,
                    compare_transfer_url,
                ) in compare_transfer_urls.items():
                    if source_record_id == compare_record_id:
                        continue
                    if source_transfer_url == compare_transfer_url:
                        _source_media_type = source_media_type.split("/")[-1]
                        _compare_media_type = compare_media_type.split("/")[-1]
                        print(
                            f"Transfer URL in record [{source_record_id[:8]}] for format [{_source_media_type}] URL in record [{compare_record_id[:8]}], format [{_compare_media_type}]"
                        )


def main():
    print(f"Checking records at: {metadata_records_path.resolve()}")

    records = load_metadata_records(records_path=metadata_records_path)
    transfer_option_urls: Dict[str, Dict[str, str]] = {}

    for record_id, record_config in records.items():
        transfer_option_urls[record_id] = get_transfer_option_urls(
            record_config=record_config
        )

    list_non_unique_transfer_option_urls(transfer_urls_by_record=transfer_option_urls)

    print("Script exited normally.")


if __name__ == "__main__":
    main()
