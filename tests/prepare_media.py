#!/usr/bin/env python
import shutil
from pathlib import Path


def copy_file(
    folder: Path, *ps: Path, force=False, base_dir=Path(__file__).parent.parent
) -> None:
    if folder.exists():
        if not force:
            return
    else:
        folder.mkdir(parents=True)
    for p in ps:
        dst = folder / p.name
        shutil.copyfile(p, dst)
        print(f"File copied: {p.relative_to(base_dir)} --> {dst.relative_to(base_dir)}")


def main():
    root = Path(__file__).parent
    src = root / "static_with_favicon/static"
    swagger_ui_files = list(src.glob("swagger-ui*"))
    redoc_file = src / "redoc.standalone.js"
    favicon_file = src / "favicon.ico"

    copy_file(root / "static_auto" / "static", *swagger_ui_files)
    copy_file(root / "static_favicon_without_swagger_ui/static", favicon_file)
    pri_cdn = root / "private_cdn/cdn"
    copy_file(pri_cdn / "swagger-ui@latest", *swagger_ui_files)
    copy_file(pri_cdn / "redoc/next", redoc_file)
    pri_cdn2 = root / "cdn_with_default_asset_path/cdn"
    copy_file(pri_cdn2 / "swagger-ui-dist@5.9.0", *swagger_ui_files)
    copy_file(pri_cdn2 / "redoc@next/bundles", redoc_file)
    simple_path = root / "simple_asset_path/cdn"
    copy_file(simple_path, redoc_file, favicon_file, *swagger_ui_files)


if __name__ == "__main__":
    main()
