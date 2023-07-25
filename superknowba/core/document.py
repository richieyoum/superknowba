from io import BytesIO
from typing import List, Any, Optional
import re
from pypdf import PdfReader
from langchain.docstore.document import Document
from hashlib import md5
from abc import abstractmethod, ABC
import docx2txt
from datetime import datetime
import pandas as pd


class File(ABC):
    def __init__(
        self,
        name: str,
        id: str,
        metadata: Optional[dict[str, Any]] = {},
        docs: Optional[List[Document]] = [],
    ):
        self.name = name
        self.id = id
        self.metadata = metadata or {}
        self.docs = docs or []

    @classmethod
    @abstractmethod
    def from_bytes(cls, file: BytesIO) -> "File":
        """Creates a File from a BytesIO object"""

    @classmethod
    def preprocess(self, text: str) -> str:
        """Replaces consecutive newlines from a string"""
        return re.sub(r"\s*\n\s*", "\n", text)

    def __repr__(self) -> str:
        return (
            f"File(name={self.name}, id={self.id},"
            " metadata={self.metadata}, docs={self.docs})"
        )

    def __str__(self) -> str:
        return f"File(name={self.name}, id={self.id}, metadata={self.metadata})"


class PdfFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "PdfFile":
        pdf_reader = PdfReader(file)
        docs = []
        for idx, page in enumerate(list(pdf_reader.pages)):
            text = page.extract_text()
            text = cls.preprocess(text)
            doc = Document(
                page_content=text.strip(),
                metadata={
                    "source": file.name,
                    "page_number": idx + 1,
                    "total_pages": len(pdf_reader.pages),
                },
            )
            docs.append(doc)
        return cls(
            name=file.name,
            id=md5(file.read()).hexdigest(),
            metadata={"uploaded at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            docs=docs,
        )


class DocxFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "DocxFile":
        text = docx2txt.process(file)
        text = cls.preprocess(text)
        doc = Document(page_content=text.strip(), metadata={"source": file.name})
        return cls(
            name=file.name,
            id=md5(file.read()).hexdigest(),
            metadata={"uploaded at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            docs=[doc],
        )


class TxtFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "TxtFile":
        text = file.read().decode("utf-8")
        text = cls.preprocess(text)
        file.seek(0)
        doc = Document(page_content=text.strip(), metadata={"source": file.name})
        return cls(
            name=file.name,
            id=md5(file.read()).hexdigest(),
            metadata={"uploaded at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            docs=[doc],
        )


class CSVFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "CSVFile":
        df = pd.read_csv(file)
        docs = []
        for i, row in enumerate(df.values):
            content = "\n".join(
                f"{str(k).strip()}: {str(v).strip()}" for k, v in zip(df.columns, row)
            )
            doc = Document(
                page_content=content, metadata={"source": file.name, "row": i}
            )
            docs.append(doc)
        return cls(
            name=file.name,
            id=md5(file.read()).hexdigest(),
            metadata={"uploaded at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            docs=docs,
        )


def read_file(file: BytesIO) -> File:
    """Reads an uploaded file and returns a File object"""
    if file.name.lower().endswith(".docx"):
        return DocxFile.from_bytes(file)
    elif file.name.lower().endswith(".pdf"):
        return PdfFile.from_bytes(file)
    elif file.name.lower().endswith(".txt"):
        return TxtFile.from_bytes(file)
    elif file.name.lower().endswith(".csv"):
        return CSVFile.from_bytes(file)
    else:
        raise NotImplementedError(f"File type {file.name.split('.')[-1]} not supported")
