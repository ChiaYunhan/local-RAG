import pytest
import pathlib
from app.fileService import FileService


class TestFileService:
    @pytest.fixture
    def file_service(self, tmp_path):
        """Create a FileService instance with a temporary directory."""
        return FileService(str(tmp_path))

    @pytest.fixture
    def sample_files(self, tmp_path):
        """Create sample test files."""
        files = {}

        # Create a text file
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("This is a plain text file.\nWith multiple lines.")
        files['txt'] = str(txt_file)

        # Create a markdown file
        md_file = tmp_path / "sample.md"
        md_file.write_text("# Sample Markdown\n\nThis is **bold** and this is *italic*.")
        files['md'] = str(md_file)

        return files

    # Test validate_file_type
    def test_validate_file_type_valid_extensions(self, file_service):
        """Test that valid file extensions are accepted."""
        assert file_service.validate_file_type("document.pdf") is True
        assert file_service.validate_file_type("notes.txt") is True
        assert file_service.validate_file_type("readme.md") is True
        assert file_service.validate_file_type("report.docx") is True
        assert file_service.validate_file_type("old_report.doc") is True

    def test_validate_file_type_invalid_extensions(self, file_service):
        """Test that invalid file extensions are rejected."""
        assert file_service.validate_file_type("image.png") is False
        assert file_service.validate_file_type("video.mp4") is False
        assert file_service.validate_file_type("script.py") is False
        assert file_service.validate_file_type("data.json") is False
        assert file_service.validate_file_type("archive.zip") is False

    def test_validate_file_type_case_insensitive(self, file_service):
        """Test that file extension validation is case-insensitive."""
        assert file_service.validate_file_type("DOCUMENT.PDF") is True
        assert file_service.validate_file_type("Notes.TXT") is True
        assert file_service.validate_file_type("ReadMe.MD") is True

    def test_validate_file_type_no_extension(self, file_service):
        """Test files without extensions."""
        assert file_service.validate_file_type("README") is False

    # Test read_file
    def test_read_file_txt(self, file_service, sample_files):
        """Test reading a plain text file."""
        content = file_service.read_file(sample_files['txt'])
        assert "This is a plain text file." in content
        assert "With multiple lines." in content

    def test_read_file_markdown(self, file_service, sample_files):
        """Test reading a markdown file."""
        content = file_service.read_file(sample_files['md'])
        assert "# Sample Markdown" in content
        assert "**bold**" in content
        assert "*italic*" in content

    def test_read_file_invalid_type(self, file_service, tmp_path):
        """Test that reading an invalid file type raises ValueError."""
        invalid_file = tmp_path / "image.png"
        invalid_file.write_bytes(b"fake png content")

        with pytest.raises(ValueError, match="File type not allowed"):
            file_service.read_file(str(invalid_file))

    def test_read_file_not_exists(self, file_service):
        """Test that reading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            file_service.read_file("/nonexistent/path/file.txt")

    def test_read_file_valid_extension_but_not_exists(self, file_service):
        """Test reading a file with valid extension but doesn't exist."""
        with pytest.raises(FileNotFoundError):
            file_service.read_file("/tmp/nonexistent.pdf")

    # Test edge cases
    def test_empty_text_file(self, file_service, tmp_path):
        """Test reading an empty text file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        content = file_service.read_file(str(empty_file))
        assert content == ""

    def test_unicode_content(self, file_service, tmp_path):
        """Test reading files with unicode content."""
        unicode_file = tmp_path / "unicode.txt"
        unicode_file.write_text("Hello 世界 🌍", encoding='utf-8')

        content = file_service.read_file(str(unicode_file))
        assert "Hello 世界 🌍" in content

    def test_base_dir_initialization(self, tmp_path):
        """Test that FileService initializes with base_dir."""
        service = FileService(str(tmp_path))
        assert service.base_dir == str(tmp_path)
