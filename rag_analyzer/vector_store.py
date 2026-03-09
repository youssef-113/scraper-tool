from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict


class VectorStoreManager:
    """Simple vector store for semantic search using keyword and statistical matching."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []
        self.metadata: List[Dict[str, Any]] = []

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None):
        """Add documents to the vector store."""
        self.documents.extend(documents)

        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{} for _ in documents])

        # Create simple keyword-based embeddings
        for doc in documents:
            embedding = self._create_embedding(doc)
            self.embeddings.append(embedding)

    def _create_embedding(self, text: str) -> List[float]:
        """Create a simple keyword-based embedding."""
        # Normalize text
        text = text.lower()
        words = text.split()

        # Create a simple bag-of-words embedding
        # Use 100 dimensions with word frequency
        embedding = [0.0] * 100

        # Common keywords for e-commerce/data analysis
        keywords = [
            'price', 'cost', 'amount', 'value', 'total',
            'product', 'item', 'name', 'title', 'description',
            'category', 'type', 'brand', 'department', 'group',
            'rating', 'review', 'score', 'stars', 'quality',
            'quantity', 'count', 'number', 'volume', 'stock',
            'date', 'time', 'year', 'month', 'day',
            'customer', 'user', 'buyer', 'client', 'person',
            'order', 'purchase', 'sale', 'transaction', 'payment',
            'average', 'mean', 'median', 'min', 'max', 'sum',
            'high', 'low', 'top', 'best', 'worst', 'popular'
        ]

        for i, keyword in enumerate(keywords[:100]):
            if keyword in text:
                # Count occurrences
                count = text.count(keyword)
                embedding[i] = min(count / 10.0, 1.0)  # Normalize to 0-1

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

    def get_relevant_context(self, query: str, max_chars: int = 2000) -> str:
        """Get relevant context for a query."""
        results = self.similarity_search(query, k=10)

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
