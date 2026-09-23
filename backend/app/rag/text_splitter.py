import re
from typing import List
from langchain_core.documents import Document

class RecursiveCharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            if end < text_len:
                # Find best separator to break at
                best_break = -1
                for sep in self.separators:
                    if sep == "":
                        continue
                    idx = text.rfind(sep, start, end)
                    if idx != -1 and idx > start:
                        best_break = idx + len(sep)
                        break
                if best_break != -1:
                    end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_len:
                break
            start = max(start + 1, end - self.chunk_overlap)

        return chunks

    def split_documents(self, documents: List[Document]) -> List[Document]:
        result = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for idx, ch in enumerate(chunks):
                meta = doc.metadata.copy() if doc.metadata else {}
                result.append(Document(page_content=ch, metadata=meta))
        return result
