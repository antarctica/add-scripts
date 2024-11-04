from add_scripts.data import load_new_records

def get_transfer_option_urls(record: dict) -> list[tuple[str, str]]:
    transfer_option_urls = []

    for distribution in record["distribution"]:
        href = distribution["transfer_option"]["online_resource"]["href"]
        if "href" not in distribution["format"]:
            print(f"WARNING! Transfer option '{href}' has no format.href.")
        transfer_option_urls.append((distribution["format"]["href"], href))

    return transfer_option_urls



def check_transfer_options(records: list[dict]) -> tuple[dict[str, list[tuple[str, str, str]]], list[tuple[str, str]]]:
    urls_flat: list[tuple[str, str, str]] = []
    for record in records:
        record_id = record["file_identifier"]
        for item in get_transfer_option_urls(record):
            urls_flat.append((record_id, item[0], item[1]))  # record_id, media_type, url

    # check for duplicate urls
    urls_list = []
    duplicate_indexes: dict[str, list[int]] = {}
    duplicate_items: dict[str, list[tuple[str, str, str]]] = {}
    for item in urls_flat:
        urls_list.append(item[2])
    for item in urls_flat:
        indexes = [index for index, value in enumerate(urls_list) if value == item[2]]
        if len(indexes) > 1:
            duplicate_indexes[item[2]] = indexes
    for url, indexes in duplicate_indexes.items():
        duplicate_items[url] = []
        for index in indexes:
            duplicate_items[url].append(urls_flat[index])

    # # check for urls without artefacts
    missing_artefacts: list[tuple[str, str]] = []
    for item in urls_flat:
        if item[2] == "https://data.bas.ac.uk/download/":
            missing_artefacts.append((item[0], item[1]))

    return duplicate_items, missing_artefacts


def report_duplicate_urls(duplicate_items: dict[str, list[tuple[str, str, str]]]) -> None:
    if len(duplicate_items) == 0:
        print("No duplicate transfer options found.")
        return
    print(f"Duplicate transfer options for:")
    for url, items in duplicate_items.items():
        print(f"- '{url}':")
        for item in items:
            print(f"  - Record ID: {item[0]} (Media type: {item[1]})")
    print("")

def report_incomplete_urls(incomplete_items: list[tuple[str, str]]) -> None:
    if len(incomplete_items) == 0:
        print("No transfer options without artefacts found.")
        return
    print("Transfer options without artefacts:")
    for item in incomplete_items:
        print(f"- Record ID: {item[0]} (Media type: {item[1]})")
    print("")

def main() -> None:
    file_names, records = load_new_records()
    duplicates, incomplete = check_transfer_options(list(records.values()))
    report_duplicate_urls(duplicates)
    report_incomplete_urls(incomplete)

    print("Script exited normally.")


if __name__ == "__main__":
    main()
