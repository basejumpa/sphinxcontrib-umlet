import sphinx
from pathlib import Path
from typing import List

import pytest


@pytest.mark.sphinx("latex", testroot="image", srcdir="pdf_image")
def test_pdf_image(tex_images: List[Path]):
    (image,) = tex_images
    if sphinx.version_info[:2] < (7, 2):
        assert image.basename() == "SimpleClass.pdf"
    else:
        assert image.name == "SimpleClass.pdf"
