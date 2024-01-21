import shutil

from pathlib import Path

import pytest

from sphinx.application import Sphinx


SIMPLE_EXPORTED_FNAME = "umlet-bf0f85b68784bab0e62bf5902f5a46b65d71ee70.png"


@pytest.mark.sphinx("html", testroot="image", srcdir="image_notchanged")
def test_image_notchanged(content: Sphinx, make_app_with_local_user_config):
    exported = content.outdir / "_images" / "SimpleClass.svg"
    exported_timestamp = exported.stat().st_mtime
    app = make_app_with_local_user_config(srcdir=content.srcdir)
    app.build()
    assert exported.stat().st_mtime == exported_timestamp


@pytest.mark.sphinx("html", testroot="image", srcdir="image_changed")
def test_image_changed(content: Sphinx, make_app_with_local_user_config):
    simpleClass = Path(content.srcdir / "SimpleClass.uxf")
    exported = content.outdir / "_images" / "SimpleClass.svg"
    exported_timestamp = exported.stat().st_mtime
    usecase = Path(content.srcdir / "Usecase.uxf")
    shutil.copy(usecase, simpleClass)
    app = make_app_with_local_user_config(srcdir=content.srcdir)
    app.build()
    assert exported.stat().st_mtime > exported_timestamp
