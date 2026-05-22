import tiktoken
from typing import List

class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.get_encoding(encoding_name)

    def split_text(self, text: str) -> List[str]:
        tokens = self.encoder.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            i += self.chunk_size - self.chunk_overlap
            
            # Prevent infinite loops on very small edge cases
            if self.chunk_size - self.chunk_overlap <= 0:
                break
                
        return chunks

text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
