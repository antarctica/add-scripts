# SCAR Antarctic Digital Database (ADD) Release Scripts - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* script to check all transfer option URLs are unique in a set of records, to defend against #2
  [#3](https://gitlab.data.bas.ac.uk/MAGIC/add-release-scripts/-/issues/3)
* initial project with initial scripts for registering download proxy lookup items and updating related records and 
  updating release/publication dates prior to import into the ADD Metadata Toolbox / Data Catalogue
  [#1](https://gitlab.data.bas.ac.uk/MAGIC/add-release-scripts/-/issues/1)

### Fixed

* selection of per-record transfer option URLs based on registered lookup items
  [#2](https://gitlab.data.bas.ac.uk/MAGIC/add-release-scripts/-/issues/2)
