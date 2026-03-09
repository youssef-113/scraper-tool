from typing import List, Dict, Any, Optional
import numpy as np
import hashlib


class VectorStoreManager:
    """Vector store for semantic search using embeddings."""

    def __init__(self, openai_key: Optional[str] = None, groq_key: Optional[str] = None):
        self.openai_key = openai_key
        self.groq_key = groq_key
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []
        self.metadata: List[Dict[str, Any]] = []
        self.client = None
        
        # Initialize OpenAI client if key provided (for embeddings)
        if openai_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
            except Exception:
                self.client = None

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to the vector store."""
        self.documents.extend(documents)

        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{} for _ in documents])

        # Create embeddings for each document
        for doc in documents:
            embedding = self._create_embedding(doc)
            self.embeddings.append(embedding)

    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding for text."""
        # Try OpenAI embeddings if available
        if self.client:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text[:8000]  # Limit text length
                )
                return response.data[0].embedding
            except Exception:
                pass
        
        # Fallback to simple keyword-based embedding
        return self._create_keyword_embedding(text)

    def _create_keyword_embedding(self, text: str) -> List[float]:
        """Create a simple keyword-based embedding."""
        text = text.lower()
        words = text.split()
        
        # Create 384-dim embedding (standard for many models)
        embedding = [0.0] * 384
        
        # Common keywords for data analysis
        keywords = [
            'price', 'cost', 'amount', 'value', 'total', 'sum',
            'product', 'item', 'name', 'title', 'description', 'detail',
            'category', 'type', 'brand', 'department', 'group', 'class',
            'rating', 'review', 'score', 'stars', 'quality', 'grade',
            'quantity', 'count', 'number', 'volume', 'stock', 'inventory',
            'date', 'time', 'year', 'month', 'day', 'hour',
            'customer', 'user', 'buyer', 'client', 'person', 'name',
            'order', 'purchase', 'sale', 'transaction', 'payment', 'buy',
            'average', 'mean', 'median', 'min', 'max', 'sum', 'std',
            'high', 'low', 'top', 'best', 'worst', 'popular', 'trend',
            'csv', 'data', 'column', 'row', 'table', 'dataset',
            'missing', 'null', 'empty', 'valid', 'complete',
            'increase', 'decrease', 'change', 'growth', 'trend',
            'compare', 'difference', 'ratio', 'percentage', 'percent'
        ]
        
        # Hash-based distribution for better vector spread
        for word in words:
            for i, keyword in enumerate(keywords[:100]):
                if keyword in word or word in keyword:
                    # Use hash for deterministic but distributed values
                    hash_val = hashlib.md5(f"{word}_{keyword}".encode()).hexdigest()
                    embedding[i] = int(hash_val[:4], 16) / 65535.0
        
        # Add word frequency features
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        for i, (word, count) in enumerate(list(word_counts.items())[:200]):
            idx = (i + 100) % 384
            embedding[idx] = min(count / 10.0, 1.0)
        
        return embedding

    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.documents:
            return []

        query_embedding = self._create_embedding(query)

        # Calculate cosine similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k results
        results = []
        for idx, score in similarities[:k]:
            results.append({
                'content': self.documents[idx],
                'metadata': self.metadata[idx],
                'score': score
            })

        return results

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_array = np.array(a)
        b_array = np.array(b)

        dot_product = np.dot(a_array, b_array)
        norm_a = np.linalg.norm(a_array)
        norm_b = np.linalg.norm(b_array)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def get_relevant_context(self, query: str, max_chars: int = 3000) -> str:
        """Get relevant context for a query."""
        results = self.similarity_search(query, k=8)

        context_parts = []
        total_chars = 0

        for result in results:
            content = result['content']
            if total_chars + len(content) > max_chars:
                remaining = max_chars - total_chars
                context_parts.append(content[:remaining])
                break

            context_parts.append(content)
            total_chars += len(content)

        return "\n\n".join(context_parts)

    def clear(self):
        """Clear all documents."""
        self.documents = []
        self.embeddings = []
        self.metadata = []
