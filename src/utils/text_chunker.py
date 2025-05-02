import re
from typing import List, Dict, Any

class TextChunker:
    """
    Utility for chunking text into smaller pieces for processing
    """

    @staticmethod
    def chunk_by_tokens(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Chunk text by approximate token count

        Args:
            text: The text to chunk
            chunk_size: Approximate number of tokens per chunk
            overlap: Number of tokens to overlap between chunks

        Returns:
            List of text chunks
        """
        # Simple approximation: 1 token ≈ 4 characters for English text
        char_size = chunk_size * 4
        overlap_chars = overlap * 4

        # Split text into chunks
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + char_size, text_len)

            # If we're not at the end of the text, try to find a good break point
            if end < text_len:
                # Look for paragraph breaks, periods, or spaces to break on
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start + char_size // 2:
                    end = paragraph_break + 2
                else:
                    sentence_break = text.rfind('. ', start, end)
                    if sentence_break != -1 and sentence_break > start + char_size // 2:
                        end = sentence_break + 2
                    else:
                        space_break = text.rfind(' ', start, end)
                        if space_break != -1:
                            end = space_break + 1

            # Add the chunk
            chunks.append(text[start:end])

            # Move start position for next chunk, with overlap
            start = max(start, end - overlap_chars)

        return chunks

    @staticmethod
    def chunk_by_clauses(text: str) -> List[Dict[str, Any]]:
        """
        Attempt to chunk text by legal clauses

        Args:
            text: The legal document text

        Returns:
            List of dictionaries with clause number and text
        """
        # Safety check - if text is empty or None, return empty list
        if not text:
            return []

        try:
            # Simplified approach - just split by paragraphs first
            # This is more reliable and less likely to get stuck
            paragraphs = text.split('\n\n')

            # If we have very few paragraphs, try to split by newlines
            if len(paragraphs) < 3:
                paragraphs = text.split('\n')

            # If we still have very few chunks, use token-based chunking
            if len(paragraphs) < 3:
                return TextChunker._fallback_chunking(text)

            # Process paragraphs to identify clauses
            clauses = []
            clause_id = 0
            current_text = ""

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # Check if this paragraph starts with a number or section identifier
                # Simple pattern matching for clause numbers
                if re.match(r'^\d+\.|\([a-z0-9]+\)|^Section|^SECTION|^Article|^ARTICLE', para):
                    # If we have accumulated text, save it as a clause
                    if current_text:
                        clauses.append({
                            "id": str(clause_id),
                            "text": current_text,
                            "type": None,
                            "risk_score": None
                        })
                        clause_id += 1
                        current_text = para
                    else:
                        current_text = para
                else:
                    # Append to current clause
                    current_text += "\n\n" + para

            # Add the last clause if there's any text left
            if current_text:
                clauses.append({
                    "id": str(clause_id),
                    "text": current_text,
                    "type": None,
                    "risk_score": None
                })

            # If we couldn't identify any clauses, fall back to simple chunking
            if not clauses:
                return TextChunker._fallback_chunking(text)

            return clauses

        except Exception as e:
            print(f"Error in chunk_by_clauses: {e}")
            # If anything goes wrong, use the fallback method
            return TextChunker._fallback_chunking(text)

    @staticmethod
    def _fallback_chunking(text: str) -> List[Dict[str, Any]]:
        """
        Simple fallback chunking method when clause detection fails

        Args:
            text: The text to chunk

        Returns:
            List of clause dictionaries
        """
        # Just split into roughly equal chunks of about 1000 characters
        chunk_size = 1000
        chunks = []

        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk:
                chunks.append({
                    "id": f"chunk_{len(chunks) + 1}",
                    "text": chunk,
                    "type": None,
                    "risk_score": None
                })

        # If we somehow still have no chunks, create at least one
        if not chunks and text:
            chunks.append({
                "id": "chunk_1",
                "text": text,
                "type": None,
                "risk_score": None
            })

        return chunks
