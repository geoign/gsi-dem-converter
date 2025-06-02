from pathlib import Path
from gsi_dem_converter import run

def main():
    # 1) 入力に「カレントディレクトリ内のすべてのXMLファイル」をワイルドカードで指定
    inputs = ["./*.xml"]

    # 2) 出力ファイル名を指定（"out.tif" の場所は任意のパスでもOK）
    out_path = Path("out.tif")

    # 3) run() を呼び出す
    run(
        inputs=inputs,
        out_path=out_path,
        sea_at_zero=True,      # 海域を 0.0m にしたい場合は True
        workers=None,              # 並列ワーカー数。1 ならシリアル。None でもOK（CPUコア数を自動選択）
        pixel_size_hint=None,   # None のままにすると各タイルのグリッドサイズの中央値を使う
        nodata=-9999.0          # 出力ファイルに埋め込む NODATA 値（デフォルトと同じ）
    )

if __name__ == "__main__":
    main()
