import glob
import zipfile
from pathlib import Path
from typing import List, Sequence

# NODATA として使用する値
NODATA_F32 = -9999.0


def _is_fgd_xml(p: Path) -> bool:
    """
    ファイル名が FGD DEM GML (XML) らしいかを判定する。
    *.aux.xml などは除外し、拡張子が .xml、かつファイル名に "DEM" と "FG-GML" を含むものを True にする。
    """
    if p.suffix.lower() != ".xml":
        return False
    # GDAL が出力する .aux.xml などは除外
    if p.name.endswith(".aux.xml"):
        return False
    return "DEM" in p.stem and "FG-GML" in p.stem


def _expand_inputs(inputs: Sequence[str | Path]) -> List[Path]:
    """
    引数で与えられたパス／ワイルドカード／ZIP／ディレクトリを展開し、
    実際に処理すべき FGD DEM GML の XML ファイル Path のリストを返す。

    - ディレクトリだった場合は再帰検索で *.xml を探す
    - ZIP ファイルだった場合は一時フォルダに展開し、展開後フォルダ内の *.xml を探す
    - それ以外のパス文字列は glob.glob で展開して得られた各 Path に対し、
      _is_fgd_xml() をチェックして True のものをリストに加える
    """
    paths: List[Path] = []

    for pattern in inputs:
        for p_str in glob.glob(str(pattern), recursive=True):
            p = Path(p_str)

            if p.is_dir():
                # ディレクトリなら再帰的に *.xml を探索
                paths.extend([q for q in p.rglob("*.xml") if _is_fgd_xml(q)])

            elif p.suffix.lower() == ".zip":
                # ZIP は一時フォルダに全部展開し、その中の *.xml を探索
                with zipfile.ZipFile(p) as z:
                    tmp_dir = p.with_suffix("")  # 例: foo.zip → foo/
                    if not tmp_dir.exists():
                        z.extractall(tmp_dir)
                    paths.extend([q for q in tmp_dir.rglob("*.xml") if _is_fgd_xml(q)])

            else:
                # 普通のファイルなら FGD XML かチェック
                if _is_fgd_xml(p):
                    paths.append(p)

    return paths
