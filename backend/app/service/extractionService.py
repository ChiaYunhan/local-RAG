from sqlalchemy.orm import Session
import pymupdf4llm
import pathlib
from pathlib import Path
from app.db.models.document import Document
from datetime import datetime


class ExtractionService:
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.markdown_dir = self.base_path / "markdown"

    def extract_markdown(self, document: Document):
        filepath = str(document.raw_filepath)
        filename = str(document.file_name)
        markdown_filename = filename.replace(".pdf", ".md")

        now = datetime.now()
        subdir = (
            self.markdown_dir
            / f"year={now.year}"
            / f"month={now.month:02d}"
            / f"day={now.day:02d}"
        )
        subdir.mkdir(parents=True, exist_ok=True)
        markdown_filepath = subdir / markdown_filename

        markdown_content = pymupdf4llm.to_markdown(filepath)

        pathlib.Path(markdown_filepath).write_bytes(markdown_content.encode())
        return markdown_filepath
