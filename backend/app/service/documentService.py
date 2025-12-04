from app.db.repository.documentRepo import DocumentRepository
from app.db.repository.summaryRepo import SummaryRepository
from app.db.repository.chunkRepo import ChunkRepository
from app.db.repository.embeddingRepo import EmbeddingRepository

# from app.service.chunkingService import ChunkingService
# from app.service.extractionService import ExtractionService
# from app.service.summaryService import SummaryService
# from app.service.embeddingService import EmbeddingService
from app.service.fileService import FileService

from app.db.schema.document import DocumentInCreate, DocumentStatus
from app.db.schema.summary import SummaryInCreate, SummaryType, SummaryStatus
from app.db.models.document import Document

from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime


class DocumentService:
    """
    Main orchestrator for document processing pipeline
    Coordinates all services to process uploaded documents
    """

    def __init__(self, session: Session):
        # Repositories
        self.doc_repo = DocumentRepository(session)
        self.chunk_repo = ChunkRepository(session)
        self.embedding_repo = EmbeddingRepository(session)
        self.summary_repo = SummaryRepository(session)

        # Services
        self.file_service = FileService()
        # self.extraction_service = ExtractionService()
        # self.chunking_service = ChunkingService()
        # self.embedding_service = EmbeddingService()
        # self.summary_service = SummaryService()

    async def create_document(self, file: UploadFile) -> Document:
        """
        Step 1: Save file and create document record
        Returns immediately to user

        Args:
            file: Uploaded file from FastAPI

        Returns:
            Document: Created document record
        """
        # Save file to disk
        filepath = await self.file_service.save_upload(file)

        # Create document record
        doc_data = DocumentInCreate(
            file_name=file.filename or "unnamed_file",
            filepath=filepath,
            summary_status=DocumentStatus.IN_PROGRESS,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        document = self.doc_repo.create_document(doc_data)

        # Ensure all attributes are loaded before returning
        # This prevents lazy loading issues when serializing
        _ = document.document_id
        _ = document.file_name

        return document

    # async def process_document_pipeline(self, document_id: int):
    #     """
    #     Step 2: Background processing pipeline
    #     This runs asynchronously after returning response to user

    #     Args:
    #         document_id: ID of document to process
    #     """
    #     try:
    #         # Get document record
    #         document = self.doc_repo.get_document_by_id(document_id)
    #         if not document:
    #             raise ValueError(f"Document {document_id} not found")

    #         # 1. Extract text from file
    #         print(f"[Doc {document_id}] Extracting text from {document.filepath}")
    #         text = self.extraction_service.extract_text(document.filepath)

    #         # 2. Create chunks (parent-child strategy)
    #         print(f"[Doc {document_id}] Creating chunks")
    #         chunk_texts = self.chunking_service.create_chunks(text)

    #         # 3. Store chunks in database
    #         print(f"[Doc {document_id}] Storing {len(chunk_texts)} chunks")
    #         chunks = []
    #         for idx, chunk_text in enumerate(chunk_texts):
    #             chunk = self.chunk_repo.create_chunk(
    #                 document_id=document_id,
    #                 chunk_text=chunk_text,
    #                 chunk_index=idx,
    #             )
    #             chunks.append(chunk)

    #         # 4. Generate and store embeddings for each chunk
    #         print(f"[Doc {document_id}] Generating embeddings")
    #         for chunk in chunks:
    #             # Split chunk into sentences
    #             sentences = self.chunking_service.split_into_sentences(
    #                 chunk.chunk_text
    #             )

    #             # Generate and store embedding for each sentence
    #             for s_idx, sentence in enumerate(sentences):
    #                 vector = self.embedding_service.generate_embedding(sentence)

    #                 self.embedding_repo.create_embedding(
    #                     chunk_id=chunk.chunk_id,
    #                     sentence_text=sentence,
    #                     sentence_index=s_idx,
    #                     embedding_vector=vector,
    #                 )

    #         # 5. Generate summary
    #         print(f"[Doc {document_id}] Generating summary")
    #         summary_text = await self.summary_service.generate_summary(text)

    #         # 6. Save summary to file
    #         summary_filepath = await self.file_service.save_summary(
    #             summary=summary_text,
    #             doc_name=str(document.file_name),
    #             summary_type="abstractive",
    #         )

    #         # 7. Create summary record
    #         summary_data = SummaryInCreate(
    #             document_id=document_id,
    #             summary_type=SummaryType.ABSTRACTIVE,
    #             filepath=summary_filepath,
    #             summary_status=SummaryStatus.COMPLETED,
    #             created_at=datetime.now(),
    #             updated_at=datetime.now(),
    #         )
    #         self.summary_repo.create_summary(summary_data)

    #         # 8. Update document status to COMPLETED
    #         self.doc_repo.update_document_status(document_id, DocumentStatus.COMPLETED)
    #         print(f"[Doc {document_id}] Processing completed successfully")

    #     except Exception as e:
    #         # Mark document as failed
    #         print(f"[Doc {document_id}] Error: {str(e)}")
    #         self.doc_repo.update_document_status(document_id, DocumentStatus.ERROR)
    #         raise

    def get_document(self, document_id: int) -> Document:
        """
        Get document by ID

        Args:
            document_id: Document ID

        Returns:
            Document: Document record or None
        """
        return self.doc_repo.get_document_by_id(document_id)

    def get_all_documents(self, skip: int = 0, limit: int = 100):
        """
        Get all documents with pagination

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Document]: List of documents
        """
        return self.doc_repo.get_all_documents(skip=skip, limit=limit)

    def delete_document(self, document_id: int) -> bool:
        """
        Delete document and associated files

        Args:
            document_id: Document ID to delete

        Returns:
            bool: True if deleted successfully
        """
        document = self.doc_repo.get_document_by_id(document_id)
        if not document:
            return False

        # Delete physical file
        self.file_service.delete_file(str(document.filepath))

        # Delete database record (cascades to chunks, embeddings, summaries)
        return self.doc_repo.delete_document(document_id)
