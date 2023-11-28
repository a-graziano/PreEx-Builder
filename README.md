# PreExBuilder
<details>
<summary>Table of Contents</summary>

- [Overview](#overview)
- [Features](#features)
  - [Memory Layer Box](#memory-layer-box)
  - [Classification Box](#classification-box)
  - [Manage DXF Box](#manage-dxf-box)
  - [Geometry Box](#geometry-box)
  - [Metrics Box](#metrics-box)
  - [Extra Box](#extra-box)
  - [Manage Attribute Table Box](#manage-attribute-table-box)
  - [Post-ex Box](#post-ex-box)

</details>

## Overview

The PreExBuilder plugin simplifies the management of DXF files exported from GPS. It aids in converting these files into shapefiles and polygons. Additionally, it assists in creating shapefiles from scratch, allowing digitization of pre-existing features. The tool provides classification by type, dimension extrapolation, and the creation of a polygon layer highlighting archaeological interventions on a specific day.

## Features

### Memory Layer Box

Generates a memory file with predefined columns such as Pre Ex, Slot, LOE. Allows duplication of active layers and selected features into a memory layer.

### Classification Box

Classifies shapefiles based on interpretation (e.g., Linear, Pit, Posthole) and status (complete, ongoing, to be done), as well as time-based classifications (0 to +2 days).

### Manage DXF Box

Converts DXF files into memory shapefiles and polygon memory shapefiles. Adds an 'Interpr' column for efficient classification of the new polygon shapefile.

### Geometry Box

Calculates area, length, and diameter of various features.

### Metrics Box

Estimates excavation area (in square meters) based on percentage allocation for different elements (e.g., Linear 10%, Pit 50%). Also, assists in estimating the number of sections and plans to be produced (work in progress).

### Extra Box

Includes functionality to generate x,y coordinates for each polygon feature (Centroids button) and assign unique IDs based on row numbers (ID button).

### Manage Attribute Table Box

Enables users to add columns in the pre-existing layer if they do not exist.

### Post-ex Box

Facilitates the quick creation of post-ex plans and applies styles to exported DXF files (post_ex data).
