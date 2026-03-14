from typing import List, Dict, Any, Optional
from openai import OpenAI


class ChatEngine:
    """AI-powered chat engine for data analysis using Groq."""

    def __init__(self, groq_api_key: str, vector_store=None, model: str = "llama-3.3-70b-versatile"):
        self.groq_api_key = groq_api_key
        self.vector_store = vector_store
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        self.client: Optional[OpenAI] = None
        self._init_error: Optional[str] = None

        if groq_api_key:
            try:
                self.client = OpenAI(
                    api_key=groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                # Test the client with a simple call
                self._test_connection()
            except Exception as e:
                self.client = None
                self._init_error = str(e)
                print(f"ChatEngine initialization error: {e}")
    
    def _test_connection(self):
        """Test the Groq API connection"""
        try:
            # Simple test to verify connection works
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            raise Exception(f"API connection test failed: {e}")

    def query(self, question: str, data_summary: str, max_context_chunks: int = 5, temperature: float = 0.3) -> str:
        """Process a user question and return an answer using Groq."""
        if not self.client:
            error_msg = f"Error: Groq API client not initialized. "
            if self._init_error:
                error_msg += f"Init error: {self._init_error}"
            elif not self.groq_api_key:
                error_msg += "No API key provided."
            else:
                error_msg += "Unknown initialization error."
            return error_msg

        # Get relevant context from vector store
        context = ""
        if self.vector_store:
            context = self.vector_store.get_relevant_context(question)

        # Build the prompt
        system_prompt = """You are a helpful data analysis assistant powered by Groq AI. You help users understand and analyze their data.
Answer questions based on the provided data summary and context.
Be concise, accurate, and helpful. If you don't have enough information, say so.

When answering:
1. Use the provided data context
2. Be specific with numbers and facts when available
3. If the question is about statistics, provide clear calculations
4. Suggest follow-up questions when appropriate
5. Use markdown formatting for better readability"""

        user_prompt = f"""Data Summary:
{data_summary}

Relevant Context from Data:
{context}

User Question: {question}

Please provide a helpful, detailed answer based on the data."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Add conversation history (last 3 exchanges)
        for msg in self.conversation_history[-6:]:
            messages.append(msg)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1024
            )

            answer = response.choices[0].message.content.strip()

            # Store in history
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})

            return answer

        except Exception as e:
            return f"Error generating response: {str(e)}"

    def change_model(self, new_model: str):
        """Change the Groq model."""
        self.model = new_model

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def suggest_questions(self, data_summary: str) -> List[str]:
        """Generate suggested questions based on data."""
        suggestions = [
            "What is the average price of products?",
            "How many unique categories are there?",
            "What are the top 5 most expensive items?",
            "Show me products with rating above 4.5",
            "What is the price range for each category?",
            "Which brand has the most products?",
            "Summarize the key insights from this data",
            "What is the distribution of ratings?",
            "Are there any missing values in the dataset?",
            "What are the most common product names?"
        ]

        # Customize based on data summary
        if "price" in data_summary.lower():
            suggestions.extend([
                "What is the price distribution?",
                "Are there any outliers in pricing?"
            ])

        if "category" in data_summary.lower():
            suggestions.extend([
                "Which category has the highest average price?",
                "How many items in each category?"
            ])

        return suggestions[:8]
