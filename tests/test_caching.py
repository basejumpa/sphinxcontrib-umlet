from pathlib import Path
from typing import List

import pytest
import sphinx

from sphinx.application import Sphinx


@pytest.mark.sphinx("latex", testroot="image", srcdir="image_latex_then_html")
def test_image_latex_then_html(
    content: Sphinx, tex_images: List[Path], make_app_with_local_user_config
):
    simpleClass_pdf = tex_images[0]
    if sphinx.version_info[:2] < (7, 2):
        assert simpleClass_pdf.basename() == "SimpleClass.pdf"
    else:
        assert simpleClass_pdf.name == "SimpleClass.pdf"
    assert simpleClass_pdf.exists()
    html_app = make_app_with_local_user_config(srcdir=content.srcdir)
    html_app.build()
    SimpleClass_svg = html_app.outdir / "_images" / "SimpleClass.svg"
    assert SimpleClass_svg.exists()
