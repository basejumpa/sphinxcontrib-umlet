import os
import os.path
import platform
import shutil
import subprocess
from hashlib import sha1
from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import TemporaryFile
from time import sleep
from typing import Dict, Any, List
from xml.etree import ElementTree as ET

from docutils import nodes
from docutils.nodes import Node, image as docutils_image
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.images import Image
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.config import Config, ENUM
from sphinx.directives.patches import Figure
from sphinx.errors import SphinxError
from sphinx.transforms.post_transforms.images import ImageConverter, get_filename_for
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset

__version__ = "1.0.2"

logger = logging.getLogger(__name__)

VALID_OUTPUT_FORMATS = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
}


class UMLetError(SphinxError):
    category = "UMLet Error"


def format_spec(argument: Any) -> str:
    return directives.choice(argument, list(VALID_OUTPUT_FORMATS.keys()))


def is_valid_format(format: str, builder: Builder) -> str:
    mimetype = VALID_OUTPUT_FORMATS.get(format, None)

    if format is None:
        return None
    elif mimetype is None:
        raise UMLetError(f"export format '{format}' is unsupported by UMLet")
    elif mimetype not in builder.supported_image_types:
        raise UMLetError(
            f"invalid export format '{format}' specified for builder '{builder.name}'"
        )
    else:
        return format


def boolean_spec(argument: Any) -> bool:
    if argument == "true":
        return True
    elif argument == "false":
        return False
    else:
        raise ValueError("unexpected value. true or false expected")


def traverse(nodes):
    for node in nodes:
        yield node
        yield from traverse(node.children)


class UMLetBase(SphinxDirective):
    option_spec = {
        "format": format_spec,
    }

    def run(self) -> List[Node]:
        nodes = super().run()
        for node in traverse(nodes):
            if isinstance(node, docutils_image):
                image = node
                break
        image["classes"].append("umlet")
        return nodes


class UMLetImage(UMLetBase, Image):
    option_spec = Image.option_spec.copy()
    option_spec.update(UMLetBase.option_spec)


class UMLetFigure(UMLetBase, Figure):
    option_spec = Figure.option_spec.copy()
    option_spec.update(UMLetBase.option_spec)


class UMLetConverter(ImageConverter):
    conversion_rules = [
        # automatic conversion based on the builder's supported image types
        ("application/x-umlet", "image/png"),
        ("application/x-umlet", "image/jpeg"),
        ("application/x-umlet", "image/svg+xml"),
        ("application/x-umlet", "application/pdf"),
        # when the export format is explicitly defined
        ("application/x-umlet-png", "image/png"),
        ("application/x-umlet-jpg", "image/jpeg"),
        ("application/x-umlet-svg", "image/svg+xml"),
        ("application/x-umlet-pdf", "application/pdf"),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        format = self.config.umlet_builder_export_format.get(self.app.builder.name)

        self._default_export_format = is_valid_format(format, self.app.builder)

    @property
    def imagedir(self) -> str:
        return os.path.join(self.app.doctreedir, "umlet")

    def is_available(self) -> bool:
        """Confirms the converter is available or not."""
        return True

    def guess_mimetypes(self, node: nodes.image) -> List[str]:
        if "umlet" in node["classes"]:
            node_format = is_valid_format(node.get("format"), self.app.builder)
            format = node_format or self._default_export_format
            extra = f"-{format}" if format else ""
            return ["application/x-umlet" + extra]
        else:
            return []

    def handle(self, node: nodes.image) -> None:
        """Render umlet file into an output image file."""
        _from, _to = self.get_conversion_rule(node)

        if _from in node["candidates"]:
            srcpath = node["candidates"][_from]
        else:
            srcpath = node["candidates"]["*"]

        abs_srcpath = Path(self.app.srcdir) / srcpath
        if not os.path.exists(abs_srcpath):
            return

        options = node.attributes
        out_filename = get_filename_for(srcpath, _to)
        destpath = str(self._umlet_export(abs_srcpath, options, out_filename))
        if "*" in node["candidates"]:
            node["candidates"]["*"] = destpath
        else:
            node["candidates"][_to] = destpath
        node["uri"] = destpath

        self.env.original_image_uri[destpath] = srcpath
        self.env.images.add_file(self.env.docname, destpath)

    def _umlet_export(self, input_abspath, options, out_filename):
        builder = self.app.builder
        input_relpath = input_abspath.relative_to(builder.srcdir)

        # Any directive options which would change the output file would go here
        unique_values = (
            # This ensures that the same file hash is generated no matter the build directory
            # Mainly useful for pytest, as it creates a new build directory every time
            str(input_relpath)
        )
        hash_key = "\n".join(unique_values)
        sha_key = sha1(hash_key.encode()).hexdigest()
        export_abspath = Path(self.imagedir) / sha_key / out_filename
        export_abspath.parent.mkdir(parents=True, exist_ok=True)
        export_relpath = export_abspath.relative_to(builder.doctreedir)
        output_format = export_abspath.suffix[1:]

        if (
            export_abspath.exists()
            and export_abspath.stat().st_mtime > input_abspath.stat().st_mtime
        ):
            return export_abspath

        if platform.system() == "Windows":
            umlet_binary = "Umlet.exe"
        else:
            umlet_binary = "umlet.sh"

        umlet_in_path = shutil.which(umlet_binary)

        if builder.config.umlet_binary_path:
            binary_path = builder.config.umlet_binary_path
        elif umlet_in_path:
            binary_path = umlet_in_path
        else:
            raise UMLetError("No UMLet executable found")

        umlet_args = [
            binary_path,
            "-action=convert",
            f"-format={output_format}",
            f"-filename={str(input_abspath)}",
            f"-output={str(export_abspath)}",
        ]

        new_env = os.environ.copy()

        logger.info(f"(umlet) '{input_relpath}' -> '{export_relpath}'")
        try:
            ret = subprocess.run(
                umlet_args, stderr=PIPE, stdout=PIPE, check=True, env=new_env
            )
        except OSError as exc:
            raise UMLetError(
                "umlet ({args}) exited with error:\n{exc}".format(
                    args=" ".join(umlet_args), exc=exc
                )
            )
        except subprocess.CalledProcessError as exc:
            raise UMLetError(
                "umlet ({args}) exited with error:\n[stderr]\n{stderr}"
                "\n[stdout]\n{stdout}\n[returncode]\n{returncode}".format(
                    args=" ".join(umlet_args),
                    stderr=exc.stderr,
                    stdout=exc.stdout,
                    returncode=exc.returncode,
                )
            )
        if not export_abspath.exists():
            raise UMLetError(
                "umlet ({args}) did not produce an output file:"
                "\n[stderr]\n{stderr}\n[stdout]\n{stdout}".format(
                    args=" ".join(umlet_args), stderr=ret.stderr, stdout=ret.stdout
                )
            )
        return export_abspath


def on_build_finished(app: Sphinx, exc: Exception) -> None:
    if exc is None:
        this_file_path = os.path.dirname(os.path.realpath(__file__))
        src = os.path.join(this_file_path, "umlet.css")
        dst = os.path.join(app.outdir, "_static")
        copy_asset(src, dst)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_post_transform(UMLetConverter)
    app.add_directive("umlet-image", UMLetImage)
    app.add_directive("umlet-figure", UMLetFigure)
    app.add_config_value("umlet_builder_export_format", {}, "html", dict)
    app.add_config_value("umlet_binary_path", None, "html")

    # Add CSS file to the HTML static path for add_css_file
    app.connect("build-finished", on_build_finished)
    app.add_css_file("umlet.css")

    return {"version": __version__, "parallel_read_safe": True}
