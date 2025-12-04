from fastapi import UploadFile
from datetime import datetime
import os
import uuid
from pathlib import Path


class FileService:
    def __init__(self, base_path: str = "./storage"):
        """
        Initialize file service with storage paths

        Args:
            base_path: Base directory for all file storage
        """
        self.base_path = Path(base_path)
        self.uploads_dir = self.base_path / "uploads"
        self.summaries_dir = self.base_path / "summaries"

        # Create directories if they don't exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> str:
        """
        Save uploaded file with unique name to prevent collisions

        Args:
            file: FastAPI UploadFile object

        Returns:
            str: Absolute filepath where file was saved
        """
        # Create date-based subdirectory
        now = datetime.now()
        subdir = (
            self.uploads_dir
            / f"year={now.year}"
            / f"month={now.month:02d}"
            / f"day={now.day:02d}"
        )
        subdir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename and add UUID to prevent collisions
        safe_filename = self._sanitize_filename(file.filename or "unnamed_file")
        unique_filename = f"{uuid.uuid4()}_{safe_filename}"
        filepath = subdir / unique_filename

        # Save file
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        return str(filepath.absolute())

    async def save_summary(
        self, summary: str, doc_name: str, summary_type: str = "abstractive"
    ) -> str:
        """
        Save summary text to file

        Args:
            summary: Summary text content
            doc_id: Document ID this summary belongs to
            summary_type: Type of summary (abstractive/extractive)

        Returns:
            str: Absolute filepath where summary was saved
        """
        # Create date-based subdirectory
        now = datetime.now()
        subdir = (
            self.summaries_dir
            / f"year={now.year}"
            / f"month={now.month:02d}"
            / f"day={now.day:02d}"
        )
        subdir.mkdir(parents=True, exist_ok=True)

        # Create filename
        filename = f"{summary_type}_summary.txt"
        filepath = subdir / doc_name / filename

        # Save summary
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(summary)

        return str(filepath.absolute())

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        # Get just the filename, no directory components
        safe_name = os.path.basename(filename)

        # Remove any remaining dangerous characters
        safe_name = safe_name.replace("..", "").replace("/", "").replace("\\", "")

        return safe_name or "unnamed_file"

    def delete_file(self, filepath: str) -> bool:
        """
        Delete a file

        Args:
            filepath: Path to file to delete

        Returns:
            bool: True if deleted, False if file didn't exist
        """
        try:
            path = Path(filepath)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filepath}: {str(e)}")
            return False
