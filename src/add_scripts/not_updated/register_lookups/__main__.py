import json
from copy import copy
from typing import Dict, List
from uuid import uuid4
from pathlib import Path

import requests
from requests_auth_aws_sigv4 import AWSSigV4


# table1 = """| Dataset Title            | Resource ID |
# | ------------------------ | ----------- |
# | Coastline, Polygon, High | `0be5339c-9d35-44c9-a10f-da4b5356840b`|
# | Coastline, Polygon, Medium | `cc111b81-5066-42dd-be60-9f05abcb5873`|
# | Coastline, Lines, High | `70ac5759-34ee-4f39-9069-2116db592340`|
# | Coastline, Lines, Medium | `480d9361-4254-4250-9c3f-3342fbdabe5e`|
# | Coastline, Seamask, High | `80700299-3691-43ec-809e-a22ddb63c66e `|
# | Coastline, Seamask, medium | `6fbd2490-44de-4a81-81c3-a1ef0c941fe3`|"""

table1 = """| Dataset Title            | Resource ID |
| ------------------------ | ----------- |
| High resolution vector polylines | `45c3cc90-098b-45e3-a809-16b80eed4ec2`|
| Medium resolution vector polylines | `f2792d06-1e9d-4e00-a5c6-37d43bee5297`|
| High resolution vector polygons | `9b4fab56-4999-4fe1-b17f-1466e41151c4`|
| Medium resolution vector polygons | `aaec1295-b0a8-4c49-a751-d964c326ce8d`|
| High resolution seamask | `b6c8848c-2513-403d-ba60-59f27556d29e`|
| Medium resolution seamask | `c3e8a5f5-a858-4df0-b7b5-217218ad920c`|"""

# table2a = """| Dataset Title            | File Type                  | Direct Link |
# | ------------------------ | -------------------------- | ----------- |
# | High resolution vector polylines | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_6.shp.zip?entryid=synth%3A45174e8c-7ce8-4d87-a6f7-570db476c6c9%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N182LnNocC56aXA%3D |
# | High resolution vector polylines | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_6.gpkg?entryid=synth%3A45174e8c-7ce8-4d87-a6f7-570db476c6c9%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N182Lmdwa2c%3D |
# | Medium resolution vector polylines | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_6.shp.zip?entryid=synth%3A1db7f188-6c3e-46cf-a3bf-e39dbd77e14c%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3XzYuc2hwLnppcA%3D%3D |
# | Medium resolution vector polylines | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_6.gpkg?entryid=synth%3A1db7f188-6c3e-46cf-a3bf-e39dbd77e14c%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3XzYuZ3BrZw%3D%3D |
# | High resolution vector polygons | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_6.shp.zip?entryid=synth%3Ae6cf8946-e493-4c36-b4f5-58f7a2ee2a74%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N182LnNocC56aXA%3D |
# | High resolution vector polygons | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_6.gpkg?entryid=synth%3Ae6cf8946-e493-4c36-b4f5-58f7a2ee2a74%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N182Lmdwa2c%3D |
# | Medium resolution vector polygons | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7_6.shp.zip?entryid=synth%3Ab5eaca58-2fce-4a68-bea5-fbafd7c90fa2%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzYuc2hwLnppcA%3D%3D
# | Medium resolution vector polygons | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7_6.gpkg?entryid=synth%3Ab5eaca58-2fce-4a68-bea5-fbafd7c90fa2%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzYuZ3BrZw%3D%3D |
# | High resolution seamask | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_6.shp.zip?entryid=synth%3A96cf916d-7aa7-464c-985e-a39692d5be83%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3XzYuc2hwLnppcA%3D%3D |
# | High resolution seamask | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_6.gpkg?entryid=synth%3A96cf916d-7aa7-464c-985e-a39692d5be83%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3XzYuZ3BrZw%3D%3D |
# | Medium resolution seamask | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_6.shp.zip?entryid=synth%3A217b8fde-5664-4ff5-8f30-0cf8c1f14be7%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfNi5zaHAuemlw |
# | Medium resolution seamask | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_6.gpkg?entryid=synth%3A217b8fde-5664-4ff5-8f30-0cf8c1f14be7%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfNi5ncGtn |"""

table2a = """| Dataset Title            | File Type                  | Direct Link |
| ------------------------ | -------------------------- | ----------- |
| High resolution vector polylines | Shapefile  |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_9.shp.zip?entryid=synth%3A45c3cc90-098b-45e3-a809-16b80eed4ec2%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N185LnNocC56aXA%3D |
| High resolution vector polylines | Geopackage |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_9.gpkg?entryid=synth%3A45c3cc90-098b-45e3-a809-16b80eed4ec2%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N185Lmdwa2c%3D |
| Medium resolution vector polylines | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_9.shp.zip?entryid=synth%3Af2792d06-1e9d-4e00-a5c6-37d43bee5297%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3Xzkuc2hwLnppcA%3D%3D |
| Medium resolution vector polylines | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_9.gpkg?entryid=synth%3Af2792d06-1e9d-4e00-a5c6-37d43bee5297%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3XzkuZ3BrZw%3D%3D |
| High resolution vector polygons | Shapefile  |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_9.shp.zip?entryid=synth%3A9b4fab56-4999-4fe1-b17f-1466e41151c4%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N185LnNocC56aXA%3D |
| High resolution vector polygons | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_9.gpkg?entryid=synth%3A9b4fab56-4999-4fe1-b17f-1466e41151c4%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N185Lmdwa2c%3D |
| Medium resolution vector polygons | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7_9.shp.zip?entryid=synth%3Aaaec1295-b0a8-4c49-a751-d964c326ce8d%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3Xzkuc2hwLnppcA%3D%3D |
| Medium resolution vector polygons | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7_9.gpkg?entryid=synth%3Aaaec1295-b0a8-4c49-a751-d964c326ce8d%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzkuZ3BrZw%3D%3D |
| High resolution seamask | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_9.shp.zip?entryid=synth%3Ab6c8848c-2513-403d-ba60-59f27556d29e%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3Xzkuc2hwLnppcA%3D%3D |
| High resolution seamask | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_9.gpkg?entryid=synth%3Ab6c8848c-2513-403d-ba60-59f27556d29e%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3XzkuZ3BrZw%3D%3D |
| Medium resolution seamask | Shapefile  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_9.shp.zip?entryid=synth%3Ac3e8a5f5-a858-4df0-b7b5-217218ad920c%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfOS5zaHAuemlw |
| Medium resolution seamask | Geopackage | https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_9.gpkg?entryid=synth%3Ac3e8a5f5-a858-4df0-b7b5-217218ad920c%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfOS5ncGtn |"""

table2b = """| Dataset Title            |Shapefile URL |GPKG URL |
| ------------------------ | ----------- | ----------- |
| Coastline, Polygon, High | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_7.shp.zip?entryid=synth%3A0be5339c-9d35-44c9-a10f-da4b5356840b%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N183LnNocC56aXA%3D|https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_polygon_v7_7.gpkg?entryid=synth%3A0be5339c-9d35-44c9-a10f-da4b5356840b%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfcG9seWdvbl92N183Lmdwa2c%3D
| Coastline, Polygon, Medium  | https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7.shp.zip?entryid=synth%3Acc111b81-5066-42dd-be60-9f05abcb5873%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3LnNocC56aXA%3D|https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_polygon_v7_7.gpkg?entryid=synth%3Acc111b81-5066-42dd-be60-9f05abcb5873%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19wb2x5Z29uX3Y3XzcuZ3BrZw%3D%3D
| Coastline, Lines, High |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_7.shp.zip?entryid=synth%3A70ac5759-34ee-4f39-9069-2116db592340%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N183LnNocC56aXA%3D|https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_high_res_line_v7_7.gpkg?entryid=synth%3A70ac5759-34ee-4f39-9069-2116db592340%3AL2FkZF9jb2FzdGxpbmVfaGlnaF9yZXNfbGluZV92N183Lmdwa2c%3D
| Coastline, Lines, Medium |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_7.shp.zip?entryid=synth%3A480d9361-4254-4250-9c3f-3342fbdabe5e%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3Xzcuc2hwLnppcA%3D%3D |https://ramadda.data.bas.ac.uk/repository/entry/get/add_coastline_medium_res_line_v7_7.gpkg?entryid=synth%3A480d9361-4254-4250-9c3f-3342fbdabe5e%3AL2FkZF9jb2FzdGxpbmVfbWVkaXVtX3Jlc19saW5lX3Y3XzcuZ3BrZw%3D%3D
| Coastline, Seamask, High |https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_7.shp.zip?entryid=synth%3A80700299-3691-43ec-809e-a22ddb63c66e%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3Xzcuc2hwLnppcA%3D%3D|https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_high_res_v7_7.gpkg?entryid=synth%3A80700299-3691-43ec-809e-a22ddb63c66e%3AL2FkZF9zZWFtYXNrX2hpZ2hfcmVzX3Y3XzcuZ3BrZw%3D%3D
| Coastline, Seamask, medium |https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_7.shp.zip?entryid=synth%3A6fbd2490-44de-4a81-81c3-a1ef0c941fe3%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfNy5zaHAuemlw |https://ramadda.data.bas.ac.uk/repository/entry/get/add_seamask_medium_res_v7_7.gpkg?entryid=synth%3A6fbd2490-44de-4a81-81c3-a1ef0c941fe3%3AL2FkZF9zZWFtYXNrX21lZGl1bV9yZXNfdjdfNy5ncGtn|"""

lambda_endpoint = (
    "https://zrpqdlufnfqcmqmzppwzegosvu0rvbca.lambda-url.eu-west-1.on.aws/"  # staging
)
# lambda_endpoint = "https://dvej4gdfa333uci4chyhkxj3wq0fkxrs.lambda-url.eu-west-1.on.aws/"  # production

lookup_items_path = Path("lookup_items.json")


def markdown_table_to_list(table: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []

    headers = []
    for header in table.splitlines()[0].split("|"):
        if header.strip() != "":
            headers.append(header.strip())

    rows = table.splitlines()[2:]  # strip first two header rows
    for row in rows:
        values = []
        for cell in row.split("|"):
            cell = cell.strip()
            if cell == "":
                continue
            values.append(cell)

        item: Dict[str, str] = {}
        for _ in zip(headers, values):
            item[_[0]] = _[1]
        items.append(item)

    return items


def normalise_resources_table(resources: List[Dict[str, str]]) -> List[Dict[str, str]]:
    normalised_resources = []

    for resource in resources:
        normalised_resources.append(
            {
                "title": resource["Dataset Title"],
                "resource_id": resource["Resource ID"].replace("`", "").strip(),
            }
        )

    return normalised_resources


def normalise_artefacts_table(artefacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    normalised_artefacts = []

    # table type A
    if list(artefacts[0].keys()) == ["Dataset Title", "File Type", "Direct Link"]:
        for artefact in artefacts:
            media_type = None

            if artefact["File Type"].lower() == "geopackage":
                media_type = "application/geopackage+sqlite3"
            elif artefact["File Type"].lower() == "shapefile":
                media_type = "application/vnd.shp"

            normalised_artefacts.append(
                {
                    "title": artefact["Dataset Title"],
                    "media_type": media_type,
                    "origin_uri": artefact["Direct Link"],
                }
            )

        return normalised_artefacts

    # table type B
    if list(artefacts[0].keys()) == ["Dataset Title", "Shapefile URL", "GPKG URL"]:
        for artefact in artefacts:
            normalised_artefacts.append(
                {
                    "title": artefact["Dataset Title"],
                    "media_type": "application/vnd.shp",
                    "origin_uri": artefact["Shapefile URL"],
                }
            )
            normalised_artefacts.append(
                {
                    "title": artefact["Dataset Title"],
                    "media_type": "application/geopackage+sqlite3",
                    "origin_uri": artefact["GPKG URL"],
                }
            )

        return normalised_artefacts

    return normalised_artefacts


def join_resources_to_artefacts(
    resources: List[Dict[str, str]], artefacts: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    artefact_resources: List[Dict[str, str]] = []

    resources_by_title: Dict[str, Dict[str, str]] = {}
    for resource in resources:
        resources_by_title[resource["title"]] = resource

    for artefact in artefacts:
        artefact_resource: Dict[str, str] = copy(artefact)
        artefact_resource["resource_id"] = resources_by_title[
            artefact_resource["title"]
        ]["resource_id"]
        artefact_resources.append(artefact_resource)

    return artefact_resources


def make_lookup_items(artefacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    lookup_items: List[Dict[str, str]] = []

    for artefact in artefacts:
        lookup_item = {
            "artefact_id": str(uuid4()),
            "resource_id": artefact["resource_id"],
            "media_type": artefact["media_type"],
            "origin_uri": artefact["origin_uri"],
        }
        lookup_items.append(lookup_item)

    return lookup_items


def register_lookup_items(lookup_items: List[Dict[str, str]]):
    for lookup_item in lookup_items:
        r = requests.post(
            url=lambda_endpoint, json=lookup_item, auth=AWSSigV4("lambda")
        )
        r.raise_for_status()
        print(f"Artefact ID: {lookup_item['artefact_id']} - {r.status_code}")


def main():
    resources = markdown_table_to_list(table1)
    resources = normalise_resources_table(resources=resources)

    artefacts = markdown_table_to_list(table2a)
    artefacts = normalise_artefacts_table(artefacts=artefacts)

    artefacts_linked = join_resources_to_artefacts(
        resources=resources, artefacts=artefacts
    )
    lookup_items = make_lookup_items(artefacts=artefacts_linked)

    print("Generated lookup items:")
    for lookup_item in lookup_items:
        print(lookup_item)

    print("")
    _input = input("Type 'y' if you are happy with the above items to be registered:")
    if _input != "y":
        print("Aborted")
        exit(0)

    print("Registering lookup items")
    register_lookup_items(lookup_items=lookup_items)
    print(f"Writing lookup items to '{lookup_items_path.resolve()}'")
    with open(lookup_items_path, mode="w") as lookup_items_file:
        json.dump(lookup_items, lookup_items_file, indent=2)


if __name__ == "__main__":
    main()
