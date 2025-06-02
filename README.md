# gsi-dem-converter
Fast and effecient tool to convert GSI FGD GML into GeoTIFF format

高速で効率的な国土地理院FGD GML(*.xml)形式の標高データをGeoTIFFに変換するツール

## Python pip で使う場合
インストール: 

`pip install gsi-dem-converter` (PyPI登録中...)

`pip install git+https://github.com/geoign/gsi-dem-converter.git` (こちらは動くはず)

コマンドラインやシェルから実行: 
`gsi-dem-convert "C:\path\to\input\*.xml" --out "C:\path\to\output\out.tif" --sea-at-zero --workers 4`

Pythonスクリプト内で呼び出し: example_python.pyを参照


## QGISで使う場合(!まだ未完成!)
プラグイン一覧から探してインストール。 

メニューのプラグインから選択してGUIを開く

## Acknowledgements
The code is based on https://github.com/MIERUNE/convert_fgd_dem_cli

ChatGPT o3 did most of the processing speed improvement.

## Credit
Fumihiko IKEGAMI (Ikegami GeoResearch)
