# Long Document Summarizer - Backend TODO

## Phase 1: Core Database & Models Setup
- [x] Create Document model with basic fields
- [x] Create Summary model with status tracking
- [x] Set up PostgreSQL with pgvector extension
- [x] Create Chunk model for parent-child retrieval (stores larger text segments)
- [x] Create Embedding model for sentence-level vectors
- [x] Add foreign key relationships (Document -> Chunk -> Embedding)
- [x] Add vector similarity indexes (HNSW or IVFFlat)
- [x] Add indexes for commonly queried fields (status, dates)

## Phase 2: File Upload & Storage
- [ ] Create file upload API endpoint (POST /api/documents/upload)
- [ ] Implement file validation (size limits, supported formats: PDF, DOCX, TXT)
- [ ] Set up local file storage directory structure
- [ ] Create file service to handle saving uploaded files to local filepath
- [ ] Generate unique filenames to prevent collisions
- [ ] Add file metadata extraction (page count, word count, file size)

## Phase 3: Document Processing Pipeline
- [ ] Create document creation service
  - [ ] Accept uploaded file
  - [ ] Create Document record in database
  - [ ] Set initial summary_status to IN_PROGRESS
  - [ ] Return document_id to client
- [ ] Implement document text extraction service
  - [ ] PDF text extraction
  - [ ] DOCX text extraction
  - [ ] TXT file reading
- [ ] Create chunking service to split documents into chunks (parent-child strategy)
  - [ ] Larger chunks for context retrieval
  - [ ] Store chunks in Chunk table
- [ ] Create sentence splitting service for embeddings
  - [ ] Split chunks into sentences
  - [ ] Generate embeddings for each sentence
  - [ ] Store embeddings in Embedding table with vector column

## Phase 4: Embedding Generation
- [ ] Set up embedding model (OpenAI, sentence-transformers, etc.)
- [ ] Create embedding service
  - [ ] Generate embeddings for sentences
  - [ ] Batch process for efficiency
  - [ ] Store vectors in Embedding table
- [ ] Implement vector similarity search functions
  - [ ] Cosine similarity queries
  - [ ] Top-k retrieval for RAG

## Phase 5: Summary Generation
- [ ] Set up LLM integration (OpenAI, Anthropic, or local model)
- [ ] Create summary service
  - [ ] Implement abstractive summarization
  - [ ] Implement extractive summarization
  - [ ] Handle chunk-by-chunk processing for large documents
  - [ ] Combine chunk summaries into final summary
- [ ] Create background job system (Celery or FastAPI BackgroundTasks)
- [ ] Implement summary status updates (IN_PROGRESS -> COMPLETED/ERROR)
- [ ] Store generated summary to local filepath
- [ ] Create Summary record linked to Document

## Phase 6: API Endpoints
- [ ] POST /api/documents/upload - Upload document and start processing
- [ ] GET /api/documents/{document_id} - Get document details and status
- [ ] GET /api/documents/{document_id}/summary - Get or retrieve summary
- [ ] GET /api/documents - List all documents with pagination
- [ ] DELETE /api/documents/{document_id} - Delete document and associated files
- [ ] PATCH /api/documents/{document_id}/retry - Retry failed summarization

## Phase 6: API Endpoints
- [ ] POST /api/documents/upload - Upload document and start processing
- [ ] GET /api/documents/{document_id} - Get document details and status
- [ ] GET /api/documents/{document_id}/summary - Get or retrieve summary
- [ ] GET /api/documents - List all documents with pagination
- [ ] DELETE /api/documents/{document_id} - Delete document and associated files
- [ ] PATCH /api/documents/{document_id}/retry - Retry failed summarization
- [ ] POST /api/documents/{document_id}/query - RAG-based Q&A endpoint
- [ ] GET /api/documents/{document_id}/search - Semantic search within document

## Phase 7: Error Handling & Resilience
- [ ] Implement retry logic for failed summarizations
- [ ] Add proper error logging
- [ ] Create error status handling and user-friendly error messages
- [ ] Add timeout handling for long-running summary operations
- [ ] Implement cleanup for orphaned files

## Phase 8: Configuration & Environment
- [ ] Set up environment variables (.env file)
  - [ ] Database URL
  - [ ] File storage path
  - [ ] LLM API keys
  - [ ] Max file size limits
- [ ] Create configuration management module
- [ ] Add requirements.txt with all dependencies

## Phase 9: Testing & Documentation
- [ ] Write unit tests for file upload service
- [ ] Write unit tests for text extraction
- [ ] Write unit tests for summarization service
- [ ] Write integration tests for complete workflow
- [ ] Create API documentation (Swagger/OpenAPI via FastAPI)
- [ ] Add README with setup instructions

## Phase 10: Optimization & Enhancement
- [ ] Add caching for frequently accessed summaries
- [ ] Implement progress tracking for long summarizations
- [ ] Add support for custom summary length preferences
- [ ] Create metrics/analytics for processing times
- [ ] Add rate limiting for API endpoints

## Future Considerations
- [ ] Support for additional file formats (markdown, HTML, EPUB)
- [ ] Multi-language document support
- [ ] Summary comparison (abstractive vs extractive)
- [ ] User authentication and document ownership
- [ ] Webhook notifications when summary is complete
- [ ] Hybrid search (combine keyword + semantic search)
- [ ] Re-ranking retrieved chunks for better RAG results
- [ ] Metadata filtering for vector search (date ranges, document types)
