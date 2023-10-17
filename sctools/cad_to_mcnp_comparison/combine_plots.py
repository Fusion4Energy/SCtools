import os
from pathlib import Path

import fitz  # imports the pymupdf library
from docx import Document
from docx.shared import Cm
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, InlineImage

FOLDER_PATH = Path(__file__).parent

TEMPLATE_FILE = FOLDER_PATH / "TEMPLATE.docx"
PDF_FILE = FOLDER_PATH / "plotm.pdf"


def get_cad_plot_paths():
    plot_paths = {}

    for file in os.listdir(FOLDER_PATH):
        if file.endswith(".jpg"):
            plot_id = int(file.split(";")[0])
            plot_paths[plot_id] = str(FOLDER_PATH / file)

    return plot_paths


def get_mcnp_plot_paths():
    plot_paths = {}

    doc = fitz.open(PDF_FILE)
    for i, page in enumerate(doc):
        page.set_rotation(90)

        mcnp_plot_pixmap = page.get_pixmap(dpi=100, clip=[260, 81, 710, 533])
        plot_file_path = str(FOLDER_PATH / f"{i}_mcnp_plot.png")
        mcnp_plot_pixmap.save(plot_file_path)

        plot_paths[i] = plot_file_path

    return plot_paths


def get_texts():
    texts = {}

    doc = fitz.open(PDF_FILE)
    for i, page in enumerate(doc):
        text = page.get_text()
        text = "basis" + text.split("basis")[-1]
        text = text.replace("\n", "")
        text = text.replace("origin", "\norigin")
        text = text.replace("extent", "\nextent")
        texts[i] = text

    return texts


def write_page(atlas, cad_plot_path, mcnp_plot_path, text):
    page = DocxTemplate(TEMPLATE_FILE)
    cad_plot = InlineImage(page, cad_plot_path, height=Cm(10))
    mcnp_plot = InlineImage(page, mcnp_plot_path, height=Cm(10))
    context = {"CAD_PLOT": cad_plot, "MCNP_PLOT": mcnp_plot, "TEXT": text}
    page.render(context)
    atlas.append(page)


def delete_mcnp_plots(plot_paths):
    for mcnp_plot in plot_paths.values():
        os.remove(mcnp_plot)


def main():
    cad_plot_paths = get_cad_plot_paths()
    mcnp_plot_paths = get_mcnp_plot_paths()
    texts = get_texts()

    atlas = Composer(Document())

    for i in range(len(cad_plot_paths)):
        write_page(atlas, cad_plot_paths[i], mcnp_plot_paths[i], texts[i])

    atlas.save(FOLDER_PATH / "result.docx")

    delete_mcnp_plots(mcnp_plot_paths)


main()
