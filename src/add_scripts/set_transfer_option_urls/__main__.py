from typing import Dict, List, Optional
from pathlib import Path
import json

from add_scripts.utils import load_metadata_records, dump_metadata_records


lookup_items_path = Path("./lookup_items.json")

metadata_records_path = Path(
    "/Users/felnne/OneDrive - NERC/Shared Documents/Projects/BAS Data Catalogue/Records/Datasets/add-7.6"
)


def load_lookup_items(lookups_path: Path) -> List[Dict[str, str]]:
    with open(lookups_path, mode="r") as lookup_items_file:
        return json.load(lookup_items_file)


def get_lookup_items_for_resource(
    resource_id: str, lookup_items: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    resource_lookup_items: List[Dict[str, str]] = []

    for lookup_item in lookup_items:
        if lookup_item["resource_id"] == resource_id:
            resource_lookup_items.append(lookup_item)

    return resource_lookup_items


def get_lookup_item_for_distribution_option(
    distribution_option: dict, lookup_items: List[Dict[str, str]]
) -> Optional[Dict[str, str]]:
    if "href" not in distribution_option["format"]:
        return None

    media_type = str(distribution_option["format"]["href"]).replace(
        "https://www.iana.org/assignments/media-types/", ""
    )
    for lookup_item in lookup_items:
        if lookup_item["media_type"] == media_type:
            return lookup_item

    return None


def set_resource_distribution_option_uris(
    resource_config: Dict, lookup_items: List[Dict[str, str]]
):
    for i, distribution_option in enumerate(resource_config["distribution"]):
        lookup_item = get_lookup_item_for_distribution_option(
            distribution_option=distribution_option, lookup_items=lookup_items
        )
        if lookup_item is None:
            continue

        distribution_option["transfer_option"]["online_resource"][
            "href"
        ] = f"https://data.bas.ac.uk/download/{lookup_item['artefact_id']}"
        resource_config["distribution"][i] = distribution_option

    return resource_config


def main():
    records = load_metadata_records(records_path=metadata_records_path)
    lookup_items = load_lookup_items(lookups_path=lookup_items_path)

    for record_id, record_config in records.items():
        record_lookup_items = get_lookup_items_for_resource(
            resource_id=record_id, lookup_items=lookup_items
        )
        records[record_id] = set_resource_distribution_option_uris(
            resource_config=record_config, lookup_items=record_lookup_items
        )

    dump_metadata_records(
        records_path=metadata_records_path,
        original_records_path=metadata_records_path,
        record_configs=list(records.values()),
    )


if __name__ == "__main__":
    main()
