import pathlib
from typing import Set
import pymupdf.layout
import pymupdf4llm
import pymupdf.pro

pymupdf.pro.unlock()


class FileService:
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".txt", ".docx", ".doc", ".md"}

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def validate_file_type(self, filepath: str) -> bool:
        """
        Validates if the file has an allowed extension.

        Args:
            filepath: Path to the file to validate

        Returns:
            True if file type is allowed, False otherwise
        """
        path = pathlib.Path(filepath)
        extension = path.suffix.lower()
        return extension in self.ALLOWED_EXTENSIONS

    def read_file(self, filepath: str) -> str:
        """
        Reads and extracts text content from a file in markdown format.

        Args:
            filepath: Path to the file to read

        Returns:
            Extracted text content as markdown string

        Raises:
            ValueError: If file type is not allowed
            FileNotFoundError: If file does not exist
        """
        if not self.validate_file_type(filepath):
            raise ValueError(f"File type not allowed: {filepath}")

        path = pathlib.Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        extension = path.suffix.lower()

        # Markdown files - already in markdown format
        if extension in {".md", ".txt"}:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        # PDF and Word documents - extract as markdown using pymupdf4llm
        elif extension in {".pdf", ".docx", ".doc"}:
            md_text = pymupdf4llm.to_markdown(filepath)
            return md_text

        else:
            raise ValueError(f"Unsupported file type: {extension}")
