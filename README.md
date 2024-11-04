# SCAR Antarctic Digital Database (ADD) Release Scripts

Scripts to assist with SCAR Antarctic Digital Database (ADD) releases.

## Purpose

To help speed up and simplify ADD releases by automating boring tasks.

Part of a wider aim to streamline and automate the ADD release workflow 
([#172](https://gitlab.data.bas.ac.uk/MAGIC/add/-/issues/172)) and more generally as a demonstration of the 
[PDC-MAGIC Data Workflows](https://gist.github.com/felnne/57b64396426bfe2ca641a91d7cf9e597) project.

## Status

**Note:** These scripts are in a raw/scrappy form, without tests, a CLI or proper structure. If and as these tasks 
settle, efforts to formalise these tasks into a proper tool may be possible.

Features, bugs, etc. for these scripts are managed in the main [ADD project](https://gitlab.data.bas.ac.uk/MAGIC/add).

## Usage

**Note:** These scripts currently contain hard-coded file paths, specific to @felnne's laptop. In time this may become 
configurable but until then, you will need to review and adjust each script before running.

To use these scripts you will need a records store which must:

- be available as `./records` relative to the root of this project (symlink's are ok)
- contain a `./records` subdirectory containing a flat list of record configs as JSON files 
  (e.g. `/records/records/abc123.json`)

**Note:** `records bulk-export` from the data catalogue can be used to dump out record configs.

**Note:** It is strongly recommended that this store be under version control, so you can easily see, and if needed 
revert, changes to records made by these scripts.

Scripts must be run in this order:

1. [clone previous records](#clone-previous-records)
1. [set resource identifiers](#set-resource-ids)
1. [update collections](#update-collections)
2. [set transfer options](#set-transfer-options)
1. [check transfer options](#check-transfer-options)
1. [set citation](#set-citation)
1. [update dates](#update-dates)

### Clone previous records

This script copies previous/current records for datasets that will be updated in an upcoming release into a folder.

Before running this script you will need to:

- decide which datasets will be updated in the upcoming release

To run this script:

```
$ poetry run python src/add_scripts/clone_records
```

For information, this script will:

- prompt for the next release version (e.g. '7.10')
- prompt for the datasets that should be cloned (datasets that typically change are selected by default)
- get the identifiers for current datasets listed in the ADD (core) collection 
- filter these against `DATASETS_TO_CLONE`
- copy selected records into new records
- removes identifiers and sets the file identifier and citation to a placeholder value
- removes distribution options except services (which are assumed to roll over)
- sets the edition to the upcoming release
- sets the `revisionOf` related record to the source record
- save cloned records as files
- save a MarkDown formatted table to act as a reference within the relevant release issue

### Set resource IDs

This script sets the resource identifier of cloned records for datasets that will be updated in an upcoming release.

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script
- copy a completed *table 1* from a release issue ('New ID' column MUST be filled in) into `next_release/table1.md`

To run this script:

```
$ poetry run python src/add_scripts/set_resource_id
```

For information, this script will:

- load cloned records and index them by ADD Dataset Code
- parse *table 1* as a MarkDown formatted string (representing a table), indexed by ADD Dataset Code
- set the file identifier and adds an identification identifier for each record based on the relevant 'New ID' value
- save each record incorporating the first segment of the record identifier as a new record
- delete the original cloned records (without the file identifier in the name)

### Update collections

This script updates the ADD core and previous versions collections based on records that will form part of the upcoming
release.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script

To run this script:

```
$ poetry run python src/add_scripts/update_collections
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- update the previous ADD (core) records collection items, to prepend the identifiers for any records that have been cloned
- update the current ADD (core) collection items, to replace the identifiers for any records that have been cloned
- update the metadata date stamp and increment the edition of the previous & current ADD records collections
- save updated collections back to the records store

### Set transfer options

This script sets distribution options (downloads) in each record in the upcoming release.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script
- copy a completed *table 2* from a release issue into `next_release/table2.md`

Any existing distribution options are not be removed, including those added by this script. This means you may need to
manually remove duplicate distribution options if running this script more than once.

**Note:** This script only supports 
[GeoPackage](https://www.iana.org/assignments/media-types/application/geopackage+sqlite3) and 
[Zipped Shapefile](https://metadata-resources.data.bas.ac.uk/media-types/application/vnd.shp+zip) as distribution 
formats.

**Note:** It is assumed all transfer options recorded in *table 2* are files deposited with PDC, and so hard-codes the
PDC contact as the distributor role.

To run this script:

```
$ poetry run python src/add_scripts/set_transfer_options
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- parse *table 2* as a MarkDown formatted string (representing a table), indexed by resource/record identifier
- process this information into distribution options, including format, transfer option (size and URL) and distributor
- append distribution options to each record
- save new records

### Check transfer options

This script checks transfer options in each record in the upcoming release have unique URLs, to detect errors from 
other tasks. This script will also check for any download proxy URLs without an artefact specified.

This script is only a check, if it finds problems they will be listed (but not fixed).

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script

To run this script:

```
$ poetry run python src/add_scripts/check_transfer_options
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- extract transfer option URLs and format media types for each record
- create a list of (record_id, transfer_url, transfer_media_type) tuples for all transfer options in all new records
- for each transfer_url find the number of times it appears in any tuple
- if more than once, store the indexes of each matching tuple (e.g. 1st and 7th list index)
- for each set of matching tuples, add to a dict indexed by transfer_option
- check whether each transfer_url points to the Download Proxy, and if so, has an artefact specified
- report on any duplicate or incomplete URLs found

### Set citation

This script sets the citation and ads an identifier for a DOI in each record in the upcoming release.

Before running this script you will need to:

- have run the [Set Resource IDs](#set-resource-ids) script
- copy a completed *table 3* from a release issue into `next_release/table3.md`

To run this script:

```
$ poetry run python src/add_scripts/set_citation
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- parse *table 3* as a MarkDown formatted string (representing a table), indexed by resource/record identifier
- process this information into a DOI identifier and 'other citation details' elements
- append the DOI identifier if not present and set the other citation details element
- save new records

### Update dates

This script updates the released and publication dates in each record in the upcoming release. It also updates the 
metadata datestamp.

All three dates will be set to the current time. UTC is always used (so in the summer will appear as 1 hour behind).

Before running this script you will need to:

- have run the [Clone Previous Records](#clone-previous-records) script

To run this script:

```
$ poetry run python src/add_scripts/set_dates
```

For information, this script will:

- load new records and index them by ADD Dataset Code
- set or update the *publication* date to the current date and time for each record
- set or update the *released* date to the current date and time for each record
- set the metadata datestamp for each record
- save each updated record

## Implementation

Each task is currently structured as its own module, within the [`add_scripts`](src/add_scripts) package.

Some common functions, enums and variables are defined in [`data.py`](src/add_scripts/data.py).

## Setup

You will need Python and Poetry installed locally to set this project for use locally.

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/add-release-scripts.git
$ cd add-release-scripts
$ poetry install
```

## Development

### Code formatting

All source code should be run through the Ruff code formatter:

```
$ poetry run ruff --format src/
```

## Licence

Copyright (c) 2022 - 2024 UK Research and Innovation (UKRI), British Antarctic Survey (BAS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
