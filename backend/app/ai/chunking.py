import tiktoken
from typing import List

class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding_name = encoding_name
        self.encoder = None

    def _get_encoder(self):
        if self.encoder is not None:
            return self.encoder

        try:
            self.encoder = tiktoken.get_encoding(self.encoding_name)
        except Exception:
            self.encoder = None
        return self.encoder

    def split_text(self, text: str) -> List[str]:
        encoder = self._get_encoder()
        if encoder is None:
            words = text.split()
            if not words:
                return []

            chunks = []
            i = 0
            while i < len(words):
                chunk = " ".join(words[i:i + self.chunk_size])
                chunks.append(chunk)
                i += self.chunk_size - self.chunk_overlap
                if self.chunk_size - self.chunk_overlap <= 0:
                    break
            return chunks

        tokens = encoder.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            i += self.chunk_size - self.chunk_overlap
            
            if self.chunk_size - self.chunk_overlap <= 0:
                break
                
        return chunks

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
