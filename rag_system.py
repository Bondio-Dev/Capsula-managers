"""
RAG система с использованием Ragbits и интеграцией с ГигаЧат
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# Ragbits импорты
from ragbits.core.embeddings.litellm import LiteLLMEmbeddings
from ragbits.core.vector_stores.in_memory import InMemoryVectorStore
from ragbits.document_search import DocumentSearch
from ragbits.core.llms.base import LLM
from ragbits.core.prompt import Prompt

# Langchain для загрузки документов
from langchain_community.document_loaders import CSVLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

import config
from gigachat_client import GigaChatClient

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        self.embedder = None
        self.vector_store = None  
        self.document_search = None
        self.llm_client = GigaChatClient()
        self.is_initialized = False
        self.stats = {
            "total_documents": 0,
            "total_chunks": 0, 
            "last_updated": None
        }

    async def initialize(self):
        """Инициализация RAG системы"""
        try:
            # Инициализация эмбеддингов
            self.embedder = LiteLLMEmbeddings(
                model=config.EMBEDDING_MODEL
            )

            # Инициализация векторного хранилища  
            self.vector_store = InMemoryVectorStore(
                embedder=self.embedder
            )

            # Инициализация системы поиска
            self.document_search = DocumentSearch(
                embedder=self.embedder,
                vector_store=self.vector_store
            )

            # Загружаем документы
            await self.load_documents()

            self.is_initialized = True
            logger.info("RAG система успешно инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации RAG системы: {e}")
            raise

    async def load_documents(self):
        """Загрузка и индексация всех документов"""
        documents = []

        # Обрабатываем CSV файлы
        csv_files = list(config.DOCUMENTS_DIR.glob("*.csv"))
        for csv_file in csv_files:
            try:
                csv_documents = await self._process_csv_file(csv_file)
                documents.extend(csv_documents)
                logger.info(f"Загружен CSV файл: {csv_file.name}")
            except Exception as e:
                logger.error(f"Ошибка загрузки {csv_file}: {e}")

        # Обрабатываем TXT файлы
        txt_files = list(config.DOCUMENTS_DIR.glob("*.txt"))  
        for txt_file in txt_files:
            try:
                txt_documents = await self._process_txt_file(txt_file)
                documents.extend(txt_documents)
                logger.info(f"Загружен TXT файл: {txt_file.name}")
            except Exception as e:
                logger.error(f"Ошибка загрузки {txt_file}: {e}")

        # Индексируем документы
        if documents:
            await self._index_documents(documents)

        # Обновляем статистику
        self.stats["total_documents"] = len(csv_files) + len(txt_files)
        self.stats["total_chunks"] = len(documents)
        self.stats["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"Загружено {len(documents)} фрагментов из {self.stats['total_documents']} файлов")

    async def _process_csv_file(self, file_path: Path) -> List[Document]:
        """Обработка CSV файла"""
        try:
            # Читаем CSV
            df = pd.read_csv(file_path, encoding='utf-8')

            # Получаем метаданные файла
            file_info = config.FILE_MAPPING.get(file_path.name, {
                "name": file_path.stem,
                "description": f"Данные из файла {file_path.name}"
            })

            documents = []

            # Преобразуем каждую строку в документ
            for index, row in df.iterrows():
                # Создаем текстовое представление строки
                content_parts = []
                for column, value in row.items():
                    if pd.notna(value):
                        content_parts.append(f"{column}: {value}")

                content = "\n".join(content_parts)

                # Создаем документ
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(file_path),
                        "file_name": file_path.name,
                        "file_type": "csv",
                        "table_name": file_info["name"],
                        "description": file_info["description"],
                        "row_index": index,
                        "total_rows": len(df)
                    }
                )
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Ошибка обработки CSV файла {file_path}: {e}")
            return []

    async def _process_txt_file(self, file_path: Path) -> List[Document]:
        """Обработка TXT файла"""
        try:
            # Читаем текстовый файл
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Получаем метаданные файла
            file_info = config.FILE_MAPPING.get(file_path.name, {
                "name": file_path.stem,
                "description": f"Текстовая информация из файла {file_path.name}"
            })

            # Разбиваем на чанки
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", ".", " ", ""]
            )

            chunks = text_splitter.split_text(content)

            # Создаем документы
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": str(file_path),
                        "file_name": file_path.name,
                        "file_type": "txt", 
                        "document_name": file_info["name"],
                        "description": file_info["description"],
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Ошибка обработки TXT файла {file_path}: {e}")
            return []

    async def _index_documents(self, documents: List[Document]):
        """Индексация документов в векторном хранилище"""
        try:
            # Конвертируем в формат Ragbits
            ragbits_documents = []
            for doc in documents:
                ragbits_doc = {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                ragbits_documents.append(ragbits_doc)

            # Индексируем в векторном хранилище
            await self.document_search.ingest(ragbits_documents)

        except Exception as e:
            logger.error(f"Ошибка индексации документов: {e}")
            raise

    async def query(self, question: str) -> Dict[str, Any]:
        """Выполнение запроса к RAG системе"""
        if not self.is_initialized:
            raise RuntimeError("RAG система не инициализирована")

        try:
            # Поиск релевантных документов
            search_results = await self.document_search.search(
                query=question, 
                limit=config.TOP_K_RETRIEVAL
            )

            # Формируем контекст
            context_parts = []
            sources = []

            for result in search_results:
                context_parts.append(result["content"])

                # Добавляем информацию об источнике
                metadata = result.get("metadata", {})
                source_info = f"{metadata.get('file_name', 'unknown')} ({metadata.get('table_name', metadata.get('document_name', 'unknown'))})"
                if source_info not in sources:
                    sources.append(source_info)

            context = "\n\n".join(context_parts)

            # Генерируем ответ через ГигаЧат
            answer = await self.llm_client.generate_answer(question, context)

            return {
                "answer": answer,
                "sources": sources,
                "context": context,
                "num_sources": len(search_results)
            }

        except Exception as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    async def get_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return self.stats.copy()
