from pathlib import Path
from typing import Sequence
import numpy as np
import multiprocessing as mp

from .parser import _parse_xml_fast
from .utils import _expand_inputs, NODATA_F32
from .io_gdal import _create_destination, _write_tile


def _worker(arg):
    """
    multiprocessing.Pool のワーカーとして、(Path, sea_at_zero) タプルを受け取り、
    _parse_xml_fast を呼び出して (mesh_code, meta, ndarray) を返す。
    """
    return _parse_xml_fast(*arg)


def run(
    inputs: Sequence[str | Path],
    out_path: str | Path,
    *,
    sea_at_zero: bool = False,
    workers: int | None = None,
    pixel_size_hint: float | None = None,
    nodata: float = NODATA_F32,
):
    """
    gsi_dem_converter のメイン処理。複数の FGD GML （XML／ZIP／ディレクトリ）をまとめて
    GeoTIFF にモザイク出力する。

    Parameters
    ----------
    inputs : Sequence[str|Path]
        対象となるファイル／フォルダ／ワイルドカード文字列のリスト
    out_path : str|Path
        出力先 GeoTIFF ファイルパス（拡張子 .tif/.tiff 推奨）
    sea_at_zero : bool, default=False
        海域の NODATA 値を 0.0m として扱う場合は True
    workers : int|None, default=None
        並列ワーカー数。1 を指定するとシングルスレッド（並列処理なし）で動作。
        None の場合は CPU コア数を自動選択。
    pixel_size_hint : float|None, default=None
        出力時のピクセルサイズ（度）。None の場合は各タイルのグリッドサイズから
        中央値を取る。
    nodata : float, default=NODATA_F32
        出力 GeoTIFF に埋め込む NODATA 値

    Raises
    ------
    SystemExit
        入力ファイルが見つからなかった場合に発生
    RuntimeError
        データパース中に必須タグが欠落していた場合など
    """

    # 入力パス群を展開し、FGD DEM XML ファイルの Path のリストを作る
    paths = _expand_inputs(inputs)
    if not paths:
        raise SystemExit("入力 XML が見つかりません")

    # 並列／直列どちらかで _worker を実行し、(mesh_code, meta, arr) を得る
    if workers is None:
        workers = max(mp.cpu_count(), 1)
    if workers == 1:
        results = [_worker((p, sea_at_zero)) for p in paths]
    else:
        with mp.Pool(processes=workers) as pool:
            results = pool.map(_worker, [(p, sea_at_zero) for p in paths])

    # メタデータと配列だけを取り出す
    # results: List[ (mesh_code:int, meta:dict, arr:np.ndarray) ]
    metas = [m for _c, m, _a in results]
    arrays = [a for _c, _m, a in results]

    # 全タイルの境界を計算 (緯度経度の最小・最大)
    min_lat = min(m["lower_corner"][0] for m in metas)
    min_lon = min(m["lower_corner"][1] for m in metas)
    max_lat = max(m["upper_corner"][0] for m in metas)
    max_lon = max(m["upper_corner"][1] for m in metas)

    # ピクセルサイズを自動決定する場合は、各タイルの幅から中央値を採用
    if pixel_size_hint is None:
        pixel_size_hint = float(
            np.median([
                (m["upper_corner"][1] - m["lower_corner"][1]) / m["grid_size"][1]
                for m in metas
            ])
        )

    # GeoTIFF を書き出すための Datasource を作成
    out_path = Path(out_path)
    ds = _create_destination(
        (min_lat, min_lon),
        (max_lat, max_lon),
        pixel_size_hint,
        out_path,
        nodata
    )

    # 各タイルの配列を適切な位置に書き込む
    for meta, arr in zip(metas, arrays):
        _write_tile(ds, meta, arr)

    # データセットを閉じることでファイルをフラッシュ
    ds = None
