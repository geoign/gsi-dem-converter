from pathlib import Path
from typing import Tuple, List

import numpy as np
from lxml import etree

from .utils import NODATA_F32


def _parse_xml_fast(path: Path, sea_at_zero: bool) -> Tuple[int, dict, np.ndarray]:
    """
    1 枚分の FGD DEM GML ファイルをストリーム解析し、
    (mesh_code, meta, ndarray) を返す。

    - mesh_code: DEM コード番号 (int)
    - meta: {
        "lower_corner": (lat_min: float, lon_min: float),
        "upper_corner": (lat_max: float, lon_max: float),
        "grid_size": (rows: int, cols: int)  # ndarray の形状
      }
    - ndarray: float32 2 次元配列（行数: grid_size[0], 列数: grid_size[1]）
    """
    mesh_code = 0
    grid_high = None
    lower_corner = None
    upper_corner = None
    tuple_bytes = None

    # XML をバイナリモードで開き、iterparse で要素を逐次読み出す
    with open(path, "rb") as fh:
        ctx = etree.iterparse(
            fh,
            events=("end",),
            tag=(
                "{http://fgd.gsi.go.jp/spec/2008/FGD_GMLSchema}DEM",
                "{http://fgd.gsi.go.jp/spec/2008/FGD_GMLSchema}coverage",
                "{http://www.opengis.net/gml/3.2}tupleList",
            ),
            recover=True,
            huge_tree=True,
        )

        for event, elem in ctx:
            tag = etree.QName(elem.tag).localname

            if tag == "DEM":
                # DEM コードを取得できれば int に変換、なければ 0
                try:
                    text = elem.findtext(".//{*}code")
                    mesh_code = int(text) if text is not None else 0
                except ValueError:
                    mesh_code = 0

            elif tag == "coverage":
                # coverage 要素から lowerCorner/upperCorner/high を取得
                lower_corner = tuple(map(float, elem.findtext(".//{*}lowerCorner").split()))
                upper_corner = tuple(map(float, elem.findtext(".//{*}upperCorner").split()))
                high = tuple(map(int, elem.findtext(".//{*}high").split()))
                # 高さ方向のグリッド数を +1 しておく
                grid_high = (high[0] + 1, high[1] + 1)

            elif tag == "tupleList":
                tuple_text = elem.text.strip() if elem.text else ""
                tuple_bytes = tuple_text.encode("utf-8", "ignore") if tuple_text else b""
                # 空の場合を明示的に扱い
                if not tuple_bytes:
                    heights_list = []  # 空リストで後続のexpected埋めへ
                else:
                    text_str = tuple_bytes.decode("utf-8", "ignore")
                    lines = text_str.splitlines()
                    heights_list: List[float] = []

            # メモリ節約のために要素をクリア
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

            # 必要な情報（tuple_bytes, grid_high）が揃ったら解析ループを抜ける
            if tuple_bytes is not None and grid_high is not None:
                break

    # coverage/tupleList 周りの情報が揃わなかった場合はエラー
    if None in (grid_high, lower_corner, upper_corner, tuple_bytes):
        raise RuntimeError(f"{path} 解析失敗: 必須タグ欠落")

    # tuple_bytes (UTF-8) を文字列に変換し、行・カンマ区切りで浮動小数点にパース
    text_str = tuple_bytes.decode("utf-8", "replace")
    lines = text_str.strip().splitlines()
    heights_list: List[float] = []

    for line in lines:
        parts = line.split(",")
        if len(parts) >= 2:
            try:
                h = float(parts[1])
            except ValueError:
                h = NODATA_F32
        else:
            h = NODATA_F32
        heights_list.append(h)

    # 期待される要素数に満たない場合は NODATA_F32 で埋める
    expected = grid_high[0] * grid_high[1]
    if len(heights_list) != expected:
        heights_list.extend([NODATA_F32] * (expected - len(heights_list)))

    elev = np.array(heights_list, dtype=np.float32)

    # sea_at_zero=True の場合は NODATA_F32→0.0 に置換
    if sea_at_zero:
        elev[elev == NODATA_F32] = 0.0

    # (rows, cols) の形状にリシェイプ
    data = elev.reshape(grid_high[::-1])

    meta = {
        "lower_corner": lower_corner,
        "upper_corner": upper_corner,
        "grid_size": grid_high[::-1],
    }

    return mesh_code, meta, data
