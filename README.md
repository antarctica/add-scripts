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

**Note:** You will need access to the MAGIC Team OneDrive/Sharepoint site to access files used by these scripts.
Scripts should be run in this order:

1. [register download proxy items](#registering-download-proxy-items)
1. [updating metadata records with download proxy URLs](#updating-metadata-records-with-download-proxy-urls)
1. [checking transfer options are unique](#checking-all-records-have-unique-transfer-option-urls)
1. [setting publication and release dates](#updating-release-and-publication-dates-in-metadata-records)

### Registering download proxy items

This script generates and registers the download URLs that will be included in metadata records for the release.

**Note:** This script assumes the information needed to create the download URLs is included in the tables within the 
ADD release issue in GitLab (specifically tables 1 and 2).

Before running this script you will need to:

1. copy and paste the contents of table 1 and 2 from the relevant ADD release issue updating the variables in the script
2. check the correct `lambda_endpoint` variable (staging or production) is uncommented (and the other is commented)

To run this script:

```
$ poetry run python src/add_scripts/register_lookups
```

For information, the steps this script performs are:

1. converting the markdown tables (table 1 & 2) in the release issue to Python objects
2. joining the objects from the two tables together (using the dataset title as a joining field)
3. converting the file type name (e.g. 'Geopackage') into a media type (e.g. 'application/geopackage+vnd.sqlite3')
4. re-formatting this combined and converted information into 
   [Download Proxy Lookup Items](https://gitlab.data.bas.ac.uk/MAGIC/add-metadata-toolbox/-/blob/main/README.md#downloads-proxy-artefacts-lookup-schema)
5. generating random artefact IDs for each lookup item
6. [registering](https://gitlab.data.bas.ac.uk/MAGIC/add-metadata-toolbox/-/blob/main/README.md#registering-downloads-proxy-artefacts-lookup-items) 
   these download items in the Downloads Proxy
7. saving the registered lookup items in a local file: `lookup_items.json`

**Note:** The artefact IDs generated for each lookup item are random, and change each time this script is run.

These URLs are registered in the 
[ADD Data Catalogue Downloads Proxy](https://gitlab.data.bas.ac.uk/MAGIC/add-metadata-toolbox/-/blob/main/README.md#user-content-downloads-proxy).

### Updating metadata records with download proxy URLs

This script takes the download URLs generated and registered in the 
[Registering Download Proxy Items](#registering-download-proxy-items) script, and adds them to the relevant metadata 
record.

Before running this script you will need to:

1. check the `lookup_items.json` file contains the right set of lookup items for the release
2. **IMPORTANT!** check the `metadata_records_path` variable points to the right release

To run this script:

```
$ poetry run python src/add_scripts/set_transfer_option_urls
```

For information, for each record in the release this script will:

1. load the metadata record from OneDrive
2. load the lookup items from `lookup_items.json`
3. find the lookup items that relate to that record (based on the resource ID)
4. for each distribution option in the metadata record, try and find a matching lookup item
5. if found, update the URL in the distribution option with the correct download URL (using on the artefact ID)
6. save the metadata record back to OneDrive

### Updating release and publication dates in metadata records

This script updates the released and publication dates in each metadata record for a release. It also updates the 
date the metadata record was last updated.

All three dates will be set to the current time (i.e. you cannot set a date in the past or future with this script). 
The date timezone used is always UTC (so in the summer will appear as 1 hour behind).

Before running this script you will need to:

1. **IMPORTANT!** check the `metadata_records_path` variable points to the right release

To run this script:

```
$ poetry run python src/add_scripts/set_dates
```

For information, for each record in the release this script will:

1. load the metadata record from OneDrive
2. set the *publication* date to the current date and time
3. set the *released* date to the current date and time
4. set the metadata updated date to the current date (times are not recorded as per the ISO specification)
5. save the metadata record back to OneDrive

### Checking all records have unique transfer option URLs

This script checks that all records in a release have unique download URLs, to detect errors in other tasks.

Before running this script you will need to:

1. check the `metadata_records_path` variable points to the right release

This script is only a check, if it finds problems they will be listed (but not fixed). If no problems are found, no 
output will be shown.

To run this script:

```
$ poetry run python src/add_scripts/check_transfer_option_urls_unique
```

For information, for each record in the release this script will:

1. load all the metadata records from OneDrive
2. for each record, and each transfer option check the transfer option URL against every other record's transfer 
   option URLs
3. discount situations where the source record ID and the comparison record ID are the same (as these will always be 
   the same)
4. log to the screen any URLs that do match, reporting the source and comparison record ID and media-type

## Implementation

Each task is currently structured as its own module, within the [`add_scripts`](src/add_scripts) package.

Some common code is shared via the [`utils`](src/add_scripts/utils.py) module.

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
