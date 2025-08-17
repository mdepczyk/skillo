import os
import shutil
from typing import Any, Dict, List, Optional

import chromadb
import numpy as np
import streamlit as st
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

from skillo.config import Config
from skillo.exceptions import (
    DocumentRetrievalError,
    DocumentStorageError,
    SimilarityCalculationError,
    VectorStoreInitializationError,
)


class VectorStore:
    """Handle ChromaDB operations for document embeddings"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.config.OPENAI_API_KEY,
            model=self.config.EMBEDDING_MODEL,
        )
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB client and collection"""
        try:
            os.makedirs(self.config.CHROMA_DB_PATH, exist_ok=True)

            self.client = chromadb.PersistentClient(
                path=self.config.CHROMA_DB_PATH,
                settings=Settings(allow_reset=True),
            )

            try:
                self.collection = self.client.get_collection(
                    name=self.config.COLLECTION_NAME
                )
            except Exception:
                self.collection = self.client.create_collection(
                    name=self.config.COLLECTION_NAME,
                    metadata={"description": "Skillo document embeddings"},
                )

        except Exception as e:
            raise VectorStoreInitializationError(
                self.config.CHROMA_DB_PATH, str(e)
            )

    def add_document(self, document: Dict[str, Any]) -> bool:
        """Add document to vector store as chunked sections"""
        try:
            if not document.get("structured_data") or not document.get(
                "structured_data", {}
            ).get("sections"):
                raise DocumentStorageError(
                    document.get("id", "unknown"),
                    self.config.COLLECTION_NAME,
                    "Document missing structured_data sections",
                )

            sections = document["structured_data"]["sections"]

            base_metadata = {
                "filename": document["metadata"]["filename"],
                "document_type": document["document_type"],
                "file_path": document["metadata"]["file_path"],
                "document_id": document["id"],
            }

            structured_data = document.get("structured_data", {})
            if "profile" in structured_data:
                base_metadata["profile"] = structured_data["profile"]

            chunk_ids = []
            chunk_embeddings = []
            chunk_documents = []
            chunk_metadatas = []

            for section_name, section_data in sections.items():
                if isinstance(section_data, list) and section_data:
                    section_content = "\n".join(f"- {item}" for item in section_data)
                elif isinstance(section_data, dict) and section_data:
                    section_content = "\n".join(f"{k}: {v}" for k, v in section_data.items())
                elif isinstance(section_data, str) and section_data.strip():
                    section_content = section_data
                else:
                    continue

                chunk_id = f"{document['id']}_{section_name}"
                embedding = self.embeddings.embed_query(section_content)
                section_metadata = base_metadata.copy()
                section_metadata["section"] = section_name

                chunk_ids.append(chunk_id)
                chunk_embeddings.append(embedding)
                chunk_documents.append(section_content)
                chunk_metadatas.append(section_metadata)

            if chunk_ids:
                self.collection.add(
                    ids=chunk_ids,
                    embeddings=chunk_embeddings,
                    documents=chunk_documents,
                    metadatas=chunk_metadatas,
                )

                st.success(
                    f"✅ Added {len(chunk_ids)} sections for {document['metadata']['filename']}"
                )
                return True
            else:
                st.warning(
                    f"No valid sections found in {document['metadata']['filename']}"
                )
                return False

        except Exception as e:
            raise DocumentStorageError(
                document.get("id", "unknown"),
                self.config.COLLECTION_NAME,
                str(e),
            )

    def get_all_documents(self, doc_type: str) -> List[Dict[str, Any]]:
        """Get basic document info for UI - lightweight, always requires doc_type"""
        if not doc_type:
            raise DocumentRetrievalError(
                "all documents",
                self.config.COLLECTION_NAME,
                "doc_type is required - specify 'cv' or 'job'",
            )

        try:

            results = self.collection.get(
                where={"document_type": doc_type}, include=["metadatas"]
            )

            unique_documents = {}

            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    document_id = metadata["document_id"]
                    if document_id not in unique_documents:
                        unique_documents[document_id] = {
                            "id": document_id,
                            "metadata": {
                                "filename": metadata["filename"],
                                "file_path": metadata["file_path"],
                            },
                            "document_type": metadata["document_type"],
                        }

            return list(unique_documents.values())

        except Exception as e:
            raise DocumentRetrievalError(
                f"{doc_type} documents", self.config.COLLECTION_NAME, str(e)
            )

    def get_all_documents_for_matching(
        self, doc_type: str
    ) -> List[Dict[str, Any]]:
        """Get documents with full structured data for matching - always requires doc_type"""
        if not doc_type:
            raise DocumentRetrievalError(
                "all documents",
                self.config.COLLECTION_NAME,
                "doc_type is required - specify 'cv' or 'job'",
            )

        try:

            results = self.collection.get(
                where={"document_type": doc_type},
                include=["documents", "metadatas"],
            )

            documents_map = {}

            if results["documents"]:
                for i in range(len(results["documents"])):
                    chunk_metadata = results["metadatas"][i]
                    document_id = chunk_metadata["document_id"]
                    section_name = chunk_metadata["section"]
                    section_content = results["documents"][i]

                    if document_id not in documents_map:
                        documents_map[document_id] = {
                            "id": document_id,
                            "metadata": {
                                "filename": chunk_metadata["filename"],
                                "file_path": chunk_metadata["file_path"],
                            },
                            "document_type": chunk_metadata["document_type"],
                            "sections": {},
                        }

                    documents_map[document_id]["sections"][
                        section_name
                    ] = section_content

            formatted_results = []
            for doc_id, document in documents_map.items():

                document["structured_data"] = {
                    "sections": document["sections"]
                }

                for i in range(len(results["metadatas"])):
                    chunk_metadata = results["metadatas"][i]
                    if (
                        chunk_metadata.get("document_id") == doc_id
                        and "profile" in chunk_metadata
                    ):
                        document["structured_data"]["profile"] = (
                            chunk_metadata["profile"]
                        )
                        break

                if doc_type == "cv":
                    personal_info = document["sections"].get("personal_information", "")
                    name = "Unknown"
                    if personal_info and ":" in personal_info:
                        for line in personal_info.split("\n"):
                            if line.strip().lower().startswith("name:"):
                                name = line.split(":", 1)[1].strip()
                                break
                    document["structured_data"]["name"] = name

                elif doc_type == "job":
                    document["structured_data"]["company"] = document["sections"].get("company", "Unknown Company")
                    document["structured_data"]["job_title"] = document["sections"].get("job_title", "Unknown Position")


                content_parts = []
                for section_data in document["sections"].values():
                    if isinstance(section_data, list):
                        content_parts.append("\n".join(f"- {item}" for item in section_data))
                    elif isinstance(section_data, dict):
                        content_parts.append("\n".join(f"{k}: {v}" for k, v in section_data.items()))
                    elif isinstance(section_data, str):
                        content_parts.append(section_data)
                document["content"] = "\n\n".join(content_parts)

                formatted_results.append(document)

            return formatted_results

        except Exception as e:
            raise DocumentRetrievalError(
                f"{doc_type} documents for matching",
                self.config.COLLECTION_NAME,
                str(e),
            )


    def get_document_count(self, doc_type: Optional[str] = None) -> int:
        """Get count of unique documents in vector store"""
        try:
            where_filter = {"document_type": doc_type} if doc_type else None
            results = self.collection.get(
                where=where_filter, include=["metadatas"]
            )

            unique_document_ids = set()
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    unique_document_ids.add(metadata["document_id"])

            return len(unique_document_ids)

        except Exception as e:
            raise DocumentRetrievalError(
                "document count", self.config.COLLECTION_NAME, str(e)
            )

    def calculate_semantic_similarity(
        self, doc1_content: str, doc2_content: str
    ) -> float:
        """Calculate semantic similarity between two documents"""
        try:

            embedding1 = self.embeddings.embed_query(doc1_content)
            embedding2 = self.embeddings.embed_query(doc2_content)

            embedding1 = np.array(embedding1)
            embedding2 = np.array(embedding2)

            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)

            similarity = dot_product / (norm1 * norm2)

            similarity = max(0, min(1, (similarity + 1) / 2))

            return float(similarity)

        except Exception as e:
            raise SimilarityCalculationError(str(e))

    def reset_database(self) -> bool:
        """Reset the vector database (delete all data)"""
        try:

            try:
                if self.collection:
                    self.client.delete_collection(
                        name=self.config.COLLECTION_NAME
                    )
                    st.info("Deleted existing collection")
            except Exception:
                st.info("Collection deletion skipped (might not exist)")

            try:
                if self.client:
                    self.client.reset()
                    st.info("Reset ChromaDB client")
            except Exception as e:
                st.warning(f"Client reset failed: {str(e)}")

            self.client = None
            self.collection = None

            try:
                if os.path.exists(self.config.CHROMA_DB_PATH):
                    shutil.rmtree(self.config.CHROMA_DB_PATH)
                    st.info("Removed database directory")
            except Exception as e:
                st.warning(f"Directory removal failed: {str(e)}")

            self._initialize_db()
            st.info("Reinitialized database")

            return True

        except Exception as e:
            st.error(f"Error resetting database: {str(e)}")
            return False
