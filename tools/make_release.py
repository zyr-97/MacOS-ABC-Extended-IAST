#!/usr/bin/env python3
"""Package a release: dist/ABC-Extended-IAST.zip and dist/release-notes.md.

Usage: python3 tools/make_release.py [vX.Y]
With a tag argument, fail unless it matches the version in build_and_verify.py.
Run by .github/workflows/release.yml when a version tag is pushed.
"""
import re
import sys
import zipfile
from build_and_verify import ROOT, VERSION, BUNDLE

DIST = ROOT / 'dist'
ZIP_NAME = 'ABC-Extended-IAST.zip'  # Unversioned, so releases/latest/download/<name> never changes.
TOP = 'ABC-Extended-IAST'           # Folder the zip unpacks into.
DOCS = ['安裝說明.txt', '符號速查.txt', '輸出對照.txt']
REPO_URL = 'https://github.com/zyr-97/MacOS-ABC-Extended-IAST'


def add(zf, path, arcname):
    """Add with fixed permissions and timestamp, so the zip is clean on macOS and reproducible."""
    if path.is_dir():
        info = zipfile.ZipInfo(arcname.rstrip('/') + '/', (2026, 1, 1, 0, 0, 0))
        info.external_attr = (0o40755 << 16) | 0x10
        zf.writestr(info, b'')
        for child in sorted(path.iterdir()):
            if child.name != '.DS_Store':
                add(zf, child, arcname.rstrip('/') + '/' + child.name)
    else:
        info = zipfile.ZipInfo(arcname, (2026, 1, 1, 0, 0, 0))
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(info, path.read_bytes())


def changelog(readme, version):
    """The '- **X.Y** — ...' line for this version from a README's changelog."""
    match = re.search(r'^- \*\*%s\*\* — (.*)$' % re.escape(version), readme, re.M)
    assert match, 'no changelog entry for %s' % version
    return match.group(1)


def main():
    if len(sys.argv) > 1:
        assert sys.argv[1] == 'v' + VERSION, 'tag %s does not match VERSION %s' % (sys.argv[1], VERSION)
    assert BUNDLE.is_dir(), BUNDLE
    DIST.mkdir(exist_ok=True)
    with zipfile.ZipFile(DIST / ZIP_NAME, 'w') as zf:
        add(zf, BUNDLE, TOP + '/' + BUNDLE.name)
        for name in DOCS:
            add(zf, ROOT / 'docs' / name, TOP + '/' + name)
        add(zf, ROOT / 'LICENSE', TOP + '/LICENSE')

    en = changelog((ROOT / 'README.md').read_text(encoding='utf-8'), VERSION)
    zh = changelog((ROOT / 'README.zh-Hant.md').read_text(encoding='utf-8'), VERSION)
    notes = f'''**ABC Extended - IAST {VERSION}**

{en}

{zh}

### Install / 安裝

1. Download **{ZIP_NAME}** below and unzip it. 下載下方的 **{ZIP_NAME}** 並解壓縮。
2. Copy **{BUNDLE.name}** into `~/Library/Keyboard Layouts/`.
   把 **{BUNDLE.name}** 複製到 `~/Library/Keyboard Layouts/`。
3. **Log out and log back in.** **登出再重新登入。**
4. Keyboard settings → Input Sources → **+** → search **IAST**. 鍵盤設定 → 輸入方式 → **＋** → 搜尋 **IAST**。

Full guide / 完整說明: [{REPO_URL}#readme]({REPO_URL}#readme) · [中文]({REPO_URL}/blob/main/README.zh-Hant.md)
'''
    (DIST / 'release-notes.md').write_text(notes, encoding='utf-8')
    print('Wrote', DIST / ZIP_NAME, 'and release-notes.md for', VERSION)


if __name__ == '__main__':
    main()
