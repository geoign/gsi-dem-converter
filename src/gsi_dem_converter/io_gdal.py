import math
from pathlib import Path

# GDAL／OSR モジュールは遅延インポートするため、まず None をセット
gdal = None
osr = None


def _ensure_gdal():
    """
    GDAL モジュールを一度だけ import し、例外モードを有効化する。
    """
    global gdal, osr
    if gdal is None:
        from osgeo import gdal as _gdal, osr as _osr
        _gdal.UseExceptions()
        # マルチスレッドの利用を GDAL 側で有効化（全 CPU コア）
        _gdal.SetConfigOption("GDAL_NUM_THREADS", "ALL_CPUS")
        gdal, osr = _gdal, _osr


def _create_destination(
    bbox_ll: tuple[float, float],
    bbox_ur: tuple[float, float],
    pixel_size: float,
    out_path: Path,
    nodata: float,
):
    """
    全体の最小緯度経度 (低緯度・低経度) と
    最大緯度経度 (高緯度・高経度)、ピクセルサイズを指定し、
    新規 GeoTIFF ファイルを作成して Dataset オブジェクトを返す。

    Parameters
    ----------
    bbox_ll : (lat_min, lon_min)
    bbox_ur : (lat_max, lon_max)
    pixel_size : float
        緯度経度のピクセルサイズ (度)
    out_path : Path
        出力先 GeoTIFF パス
    nodata : float
        書き込む NODATA 値

    Returns
    -------
    ds : gdal.Dataset
        書き込み用の Dataset。最後に None をセットするとクローズされる。
    """
    _ensure_gdal()

    # 出力画像のピクセル数を計算
    # lon 方向のピクセル数
    xsize = math.ceil((bbox_ur[1] - bbox_ll[1]) / pixel_size)
    # lat 方向のピクセル数
    ysize = math.ceil((bbox_ur[0] - bbox_ll[0]) / pixel_size)

    # GTiff ドライバを使い、1 バンド float32 の GeoTIFF を新規作成
    ds = gdal.GetDriverByName("GTiff").Create(
        str(out_path),
        xsize,
        ysize,
        1,
        gdal.GDT_Float32,
        options=["TILED=YES", "COMPRESS=LZW", "BLOCKXSIZE=256", "BLOCKYSIZE=256"],
    )

    # 回転行列なし、左上座標 (lon_min, lat_max)
    ds.SetGeoTransform((bbox_ll[1], pixel_size, 0, bbox_ur[0], 0, -pixel_size))
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    ds.SetProjection(srs.ExportToWkt())
    ds.GetRasterBand(1).SetNoDataValue(nodata)

    return ds


def _write_tile(ds, meta: dict, arr):
    """
    1 タイル分の numpy 配列 arr を、
    すでに作成済みの ds（GeoTIFF Dataset）に
    適切にクリッピングして書き込む。

    Parameters
    ----------
    ds : gdal.Dataset
        _create_destination で得られた Dataset
    meta : dict
        {
            "lower_corner": (lat_min, lon_min),
            "upper_corner": (lat_max, lon_max),
            "grid_size": (rows, cols),
        }
    arr : 2D numpy.ndarray
        形状 (rows, cols) の float32 標高データ
    """
    rows, cols = arr.shape
    gt = ds.GetGeoTransform()
    px_w = gt[1]
    px_h = abs(gt[5])

    # タイルの左上 (arr[0,0]) の座標（緯度経度）をメタから取得
    lat0, lon0 = meta["upper_corner"]
    # GeoTIFF 内のオフセットを計算（左上原点、北緯上向きなので注意）
    x_off = math.floor((lon0 - gt[0]) / px_w)
    y_off = math.floor((gt[3] - lat0) / px_h)

    ds_cols = ds.RasterXSize
    ds_rows = ds.RasterYSize

    # 右下のインデックスを計算
    x_end = x_off + cols
    y_end = y_off + rows

    # 出力画像の外側に出る場合はクリップ
    x_clip_left = max(0, -x_off)
    y_clip_top = max(0, -y_off)
    x_clip_right = max(0, x_end - ds_cols)
    y_clip_bottom = max(0, y_end - ds_rows)

    if any((x_clip_left, y_clip_top, x_clip_right, y_clip_bottom)):
        arr = arr[y_clip_top : rows - y_clip_bottom, x_clip_left : cols - x_clip_right]
        x_off += x_clip_left
        y_off += y_clip_top

    if arr.size == 0:
        return

    ds.GetRasterBand(1).WriteArray(arr, x_off, y_off)
