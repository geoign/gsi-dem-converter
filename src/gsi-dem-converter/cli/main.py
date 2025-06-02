import argparse
import sys
from pathlib import Path

# src/gsi_dem_converter/core.py に定義した run 関数を呼び出す
from gsi_dem_converter.core import run

def main():
    parser = argparse.ArgumentParser(
        prog="gsi-dem-convert",
        description="GSI FGD GML → GeoTIFF 高速コンバータ（シングルバンド float32 版）",
    )
    parser.add_argument("inputs", nargs="+", help="入力 XML / ZIP / ディレクトリ / ワイルドカード")
    parser.add_argument("--out", dest="out", required=True, help="出力先 GeoTIFF ファイル (拡張子 .tif/.tiff)")
    parser.add_argument("--sea-at-zero", action="store_true", help="海域 NODATA を 0 m に変換")
    parser.add_argument("--workers", type=int, default=None, help="並列ワーカー数 (1 でシリアル)")
    parser.add_argument("--pixel-size", type=float, help="ピクセルサイズ(度) を強制指定")
    args = parser.parse_args()

    try:
        run(
            args.inputs,
            Path(args.out),
            sea_at_zero=args.sea_at_zero,
            workers=args.workers,
            pixel_size_hint=args.pixel_size,
        )
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
