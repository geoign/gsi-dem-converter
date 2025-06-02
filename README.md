# gsi-dem-converter
Fast and effecient tool to convert GSI FGD GML into GeoTIFF format

高速で効率的な国土地理院FGD GML(*.xml)形式の標高データをGeoTIFFに変換するツール

## Install
- Python pip
`pip install gsi-dem-converter` (PyPI登録中...)
- QGIS
プラグイン一覧から探してインストール。 (!未完成!)

## 実行
- コマンドラインやシェルから
`gsi-dem-convert "C:\path\to\input\*.xml" --out "C:\path\to\output\out.tif" --sea-at-zero --workers 4`

- Pythonスクリプト内で
See example_python.py

## Acknowledgements
The code is based on https://github.com/MIERUNE/convert_fgd_dem_cli

ChatGPT o3 did most of the processing speed improvement.

## Credit
Fumihiko IKEGAMI (Ikegami GeoResearch)
