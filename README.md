# gsi-dem-converter

<!-- ![PyPI](https://img.shields.io/pypi/v/gsi-dem-converter) -->

<!-- ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg) -->

Fast & efficient converter from **GSI FGD DEM (GML \*.xml)** to **GeoTIFF** 📏➡️🗺️

高速で効率的に **国土地理院 FGD DEM (GML \*.xml)** 形式の標高データを **GeoTIFF** に変換します。

---

## Table of Contents

* [Features](#features)
* [Installation](#installation)

  * [PyPI (coming soon)](#pypi-coming-soon)
  * [GitHub](#github)
* [Usage](#usage)

  * [Command‑line](#command-line)
  * [Python](#python)
  * [QGIS Plugin $WIP$](#qgis-plugin-wip)
* [Acknowledgements](#acknowledgements)
* [Credits](#credit)
* [License](#license)

## Features

* **Ultra‑fast** multi‑threaded conversion
* Optional **sea‑level zero** fill for ocean pixels
* Both **CLI** & **Python API**
* **QGIS GUI plugin** (work in progress)

## Installation

### PyPI (coming soon)

```bash
pip install gsi-dem-converter
```

### GitHub

```bash
pip install git+https://github.com/geoign/gsi-dem-converter.git
```

## Usage

### Command‑line

```bash
# Windows example
 gsi-dem-convert "C:\path\to\input\*.xml" \
                 --out "C:\path\to\output\out.tif" \
                 --sea-at-zero \
                 --workers 4
```

### Python

```python
from gsi_dem_converter import convert

convert(
    src=r"C:\path\to\input\*.xml",
    dst=r"C:\path\to\output\out.tif",
    sea_at_zero=True,
    workers=4,
)
```

> See [`example_python.py`](./example_python.py) for a complete script.

### QGIS Plugin (WIP)

> **Status:** *Under development*
>
> When published to the QGIS Plugin Repository you will be able to:
>
> 1. Open **Plugins ▸ Manage and Install Plugins…** and search for **“GSI DEM Converter”**.
> 2. Click **Install**.
> 3. Launch the GUI from **Plugins ▸ GSI DEM Converter**.

## Acknowledgements

This tool builds upon the excellent work in [MIERUNE/convert\_fgd\_dem\_cli](https://github.com/MIERUNE/convert_fgd_dem_cli).

Performance improvements were optimized with help from **ChatGPT o3**.

## Credit

**Fumihiko IKEGAMI** / Ikegami GeoResearch

## License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.
