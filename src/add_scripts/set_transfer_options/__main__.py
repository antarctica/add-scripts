from add_scripts.data import load_new_records, save_new_records, load_table, OUTPUT_BASE

TRANSFER_OPTIONS = {
    'https://www.iana.org/assignments/media-types/application/geopackage+sqlite3': {
        "format": {
            "format": "GeoPackage",
            "href": "https://www.iana.org/assignments/media-types/application/geopackage+sqlite3"
        },
        "transfer_option": {
            "online_resource": {
                "title": "GeoPackage",
                "description": "Download information as an OGC GeoPackage.",
                "function": "download"
            }
        }
    },
    'https://metadata-resources.data.bas.ac.uk/media-types/application/vnd.shp+zip': {
        "format": {
            "format": "Shapefile (Zipped)",
            "href": "https://metadata-resources.data.bas.ac.uk/media-types/application/vnd.shp+zip"
        },
        "transfer_option": {
            "online_resource": {
                "title": "Shapefile (Zipped)",
                "description": "Download information as an Esri Shapefile (compressed as a Zip file).",
                "function": "download"
            }
        }
    }
}

PDC_DISTRIBUTOR = {
    "organisation": {
        "name": "UK Polar Data Centre, British Antarctic Survey",
        "href": "https://ror.org/01rhff309",
        "title": "ror"
    },
    "phone": "+44 (0)1223 221400",
    "address": {
        "delivery_point": "British Antarctic Survey, High Cross, Madingley Road",
        "city": "Cambridge",
        "administrative_area": "Cambridgeshire",
        "postal_code": "CB3 0ET",
        "country": "United Kingdom"
    },
    "email": "polardatacentre@bas.ac.uk",
    "online_resource": {
        "href": "https://www.bas.ac.uk/team/business-teams/information-services/uk-polar-data-centre/",
        "title": "UK Polar Data Centre (UK PDC) - BAS public website",
        "description": "General information about the NERC Polar Data Centre (UK PDC) from the British Antarctic Survey (BAS) public website.",
        "function": "information"
    },
    "role": [
        "distributor"
    ]
}

def load_table2() -> list[dict]:
    table = load_table(table_path=OUTPUT_BASE / "table2.md")

    rows_ = []
    for row in table:
        row_ = {
            'record_id': row['Resource ID'],
            'media_type': row['Media Type'],
            'size_bytes': int(row['Size (Bytes)']),
            'access_url': row['Access URL'],
        }
        rows_.append(row_)
    return rows_

def process_artefacts(rows: list[dict]) -> dict[str, list[tuple[str, int, str]]]:
    artefacts = {}

    for row in rows:
        if row['record_id'] not in artefacts:
            artefacts[row['record_id']] = []
        artefacts[row['record_id']].append((row['media_type'], row['size_bytes'], row['access_url']))

    return artefacts

def process_distribution_options(record: dict, artefacts: list[tuple[str, int, str]]) -> dict:
    if len(artefacts) == 0:
        return record

    if 'distribution' not in record:
        record['distribution'] = []
    for artefact in artefacts:
        try:
            transfer_format = TRANSFER_OPTIONS[artefact[0]]
        except KeyError as e:
            raise RuntimeError(f"Unsupported media type: '{artefact[0]}'") from e

        dist_opt = {
            'format': transfer_format['format'],
            'transfer_option': transfer_format['transfer_option'],
            'distributor': PDC_DISTRIBUTOR,
        }
        dist_opt['transfer_option']['size'] = {
          "unit": "bytes",
          "magnitude": artefact[1]
        }
        dist_opt['transfer_option']["online_resource"]['href'] = artefact[2]
        record['distribution'].append(dist_opt)

    return record

def main() -> None:
    file_names, records = load_new_records()
    artefacts = process_artefacts(rows=load_table2())
    for record_code, record in records.items():
        record_id = record['file_identifier']
        records[record_code] = process_distribution_options(record, artefacts[record_id])
    save_new_records(file_names, records)
    print("Script exited normally.")


if __name__ == "__main__":
    main()
