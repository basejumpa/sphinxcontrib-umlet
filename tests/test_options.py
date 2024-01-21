from typing import List

import pytest

from bs4 import Tag
from sphinx.application import Sphinx
from sphinx.util.images import get_image_size
from sphinxcontrib.umlet import UMLetError


@pytest.mark.sphinx("html", testroot="alt")
def test_alt(directives: List[Tag]):
    assert directives[0]["alt"] == "An Example"


@pytest.mark.sphinx("html", testroot="align")
def test_align(directives: List[Tag]):
    assert "align-left" in directives[0]["class"]
    assert "align-center" in directives[1]["class"]
    assert "align-right" in directives[2]["class"]


# noinspection PyTypeChecker
@pytest.mark.sphinx("html", testroot="width-height")
def test_width_height(directives: List[Tag]):
    assert "width: 100px;" in directives[0]["style"]
    assert "height: 100px;" in directives[1]["style"]
    assert "width: 1000px;" in directives[2]["style"]


# noinspection PyTypeChecker
@pytest.mark.sphinx("html", testroot="scale")
def test_scale(directives: List[Tag]):
    assert "width: 140.0px; height: 70.0px;" in directives[0]["style"]
    assert "width: 1400.0px; height: 700.0px;" in directives[1]["style"]
    assert "width: 70.0px; height: 35.0px;" in directives[2]["style"]
    assert "width: 280.0px; height: 140.0px;" in directives[3]["style"]
    with pytest.raises(KeyError):
        directives[4]["style"]


@pytest.mark.sphinx("html", testroot="image")
def test_image(directives: List[Tag]):
    (img,) = directives
    assert img.name == "img"
    assert img["src"] == "_images/SimpleClass.svg"
    assert img["alt"] == "_images/SimpleClass.svg"
    assert img["class"] == ["umlet"]


@pytest.mark.sphinx("html", testroot="figure")
def test_figure(content: Sphinx, directives: List[Tag]):
    filenames_sizes = [
        ("SimpleClass.png", (140, 70)),
        ("Usecase.png", (160, 80)),
    ]
    for img, (filename, size) in zip(directives, filenames_sizes):
        assert img.name == "img"
        assert img["src"] == "_images/" + filename
        assert img["alt"] == "_images/" + filename
        assert img["class"] == ["umlet"]
        image_path = content.outdir / img["src"]
        assert get_image_size(image_path) == size
        imageContainerTag = img.parent
        assert imageContainerTag.name == "figure"


@pytest.mark.sphinx("html", testroot="reference")
def test_reference(directives: List[Tag]):
    (img,) = directives
    assert img.name == "img"
    assert img["src"] == "_images/SimpleClass.svg"
    assert img["alt"] == "_images/SimpleClass.svg"
    assert img["class"] == ["umlet"]


@pytest.mark.sphinx("html", testroot="warnings")
def test_warnings(content: Sphinx, directives: List[Tag]):
    assert len(directives) == 1
    warnings = content._warning.getvalue()
    assert "image file not readable: missing.uxf" in warnings
    assert '"gif" unknown; choose from "png", "jpg", "svg", or "pdf".' in warnings
