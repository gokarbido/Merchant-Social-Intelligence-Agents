import pandas as pd
from typing import List, Dict
from agents.ollama_client import OllamaClient
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
import os
from agents.vector_backends import get_embedding, FaissIndex, ChromaDBIndex

SYSTEM_PROMPT = """
You are a merchant matchmaker for a smart social network. Given a merchant profile and a list of candidate merchants, suggest up to 5 relevant merchant IDs for networking or partnership. Only return a comma-separated list of merchant IDs from the candidate list.
"""

# Simple embedding function (replace with real model in production)
def get_embedding(text: str) -> np.ndarray:
    np.random.seed(abs(hash(text)) % (2**32))
    return np.random.rand(384)

class MatchmakerAgent:
    def __init__(self, merchant_data_path: str, pgvector_dsn: str = None):
        self.df = pd.read_csv(merchant_data_path, dtype={'merchant_id': str})
        self.llm = OllamaClient()
        self.pgvector_dsn = pgvector_dsn
        self.vector_backend = os.environ.get("VECTOR_BACKEND", "pgvector").lower()
        if self.vector_backend == "pgvector" and pgvector_dsn:
            self._init_pgvector()
        elif self.vector_backend == "faiss":
            self._init_faiss()
        elif self.vector_backend == "chromadb":
            self._init_chromadb()

    def _init_pgvector(self):
        self.conn = psycopg2.connect(self.pgvector_dsn)
        register_vector(self.conn)
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS merchant_embeddings (
                        merchant_id TEXT PRIMARY KEY,
                        embedding vector(384)
                    )
                """)
                for _, row in self.df.iterrows():
                    emb = get_embedding(row['message']).tolist()
                    cur.execute("""
                        INSERT INTO merchant_embeddings (merchant_id, embedding)
                        VALUES (%s, %s)
                        ON CONFLICT (merchant_id) DO UPDATE SET embedding = EXCLUDED.embedding
                    """, (row['merchant_id'], emb))
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def _init_faiss(self):
        self.faiss_index = FaissIndex()
        for _, row in self.df.iterrows():
            self.faiss_index.add(row['merchant_id'], row['message'])

    def _init_chromadb(self):
        self.chromadb_index = ChromaDBIndex()
        for _, row in self.df.iterrows():
            self.chromadb_index.add(row['merchant_id'], row['message'])

    def get_merchant_name(self, merchant_id: str) -> str:
        row = self.df[self.df['merchant_id'] == merchant_id]
        if not row.empty:
            return row.iloc[0].get('mcc_description', merchant_id)
        return merchant_id

    async def is_marketing_related(self, text: str) -> bool:
        """Use LLM to determine if text is related to marketing or promotion."""
        prompt = """
        Analyze if the following text in Portuguese is related to marketing, advertising, promotion, 
        social media, or digital services. Respond with only 'yes' or 'no'.
        
        Text: """ + text + """
        
        Response (yes/no): """
        
        try:
            response = await self.llm.generate(prompt, max_tokens=10)
            return 'sim' in response.lower() or 'yes' in response.lower()
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            return False

    async def find_matches(self, user_id: str, message: str, feedback_memory=None) -> List[Dict]:
        # Get user information
        user_row = self.df[self.df['merchant_id'] == user_id]
        if user_row.empty:
            return []
            
        user_city = user_row.iloc[0]['city']
        
        # Check if the message is marketing-related using LLM
        is_marketing_related = await self.is_marketing_related(message)
        
        # Find potential matches
        matches = []
        for _, row in self.df.iterrows():
            # Skip the user themselves
            if row['merchant_id'] == user_id:
                continue
                
            merchant_message = str(row['message'])
            merchant_message_lower = merchant_message.lower()
            
            # Calculate match score
            score = 0
            
            # 1. Check if both messages are marketing-related using LLM
            if is_marketing_related:
                merchant_is_marketing = await self.is_marketing_related(merchant_message)
                if merchant_is_marketing:
                    score += 10  # Strong match if both are marketing-related
            
            # 2. Check for same city
            if row['city'] == user_city:
                score += 3
                
            # 3. Check for common keywords (as fallback)
            message_words = set(message.lower().split())
            merchant_words = set(merchant_message_lower.split())
            common_words = message_words & merchant_words
            
            # Filter out common words
            common_words = {w for w in common_words if len(w) > 3 and w not in ['com', 'para', 'como', 'mais', 'muito']}
            score += len(common_words) * 2
            
            # 4. Check for service request/offer patterns
            request_indicators = ['preciso', 'busco', 'procurando', 'quero', 'precisamos', 'precisava']
            offer_indicators = ['ofereço', 'faço', 'presto', 'vendo', 'trabalho com', 'sou', 'sou de', 'atendo']
            
            is_request = any(ind in message.lower() for ind in request_indicators)
            is_offer = any(ind in merchant_message_lower for ind in offer_indicators)
            
            if is_request and is_offer:
                score += 5  # Strong match for request-offer pairs
                
            # Debug info
            debug_info = {
                'merchant_id': row['merchant_id'],
                'message': merchant_message,
                'score': score,
                'is_marketing_related': is_marketing_related,
                'common_words': list(common_words),
                'city_match': row['city'] == user_city
            }
            print(f"Debug - Merchant {row['merchant_id']} - Score: {score} - {debug_info}")
            
            # Only include matches with a minimum score
            if score >= 5:  # Adjusted threshold for LLM-based matching
                matches.append({
                    'merchant_id': row['merchant_id'],
                    'name': self.get_merchant_name(row['merchant_id']),
                    'city': row['city'],
                    'message': merchant_message,
                    'score': score
                })
        
        # Sort matches by score (highest first) and then by city (same city first)
        matches.sort(key=lambda x: (-x['score'], 0 if x['city'] == user_city else 1))
        
        # Get top 5 matches
        top_matches = matches[:5]
        
        # If no matches found, return empty list
        if not top_matches:
            return []
            
        # Format the matches for the response
        formatted_matches = []
        for match in top_matches:
            formatted_matches.append({
                'id': match['merchant_id'],
                'name': match['name'],
                'city': match['city'],
                'message': match['message']
            })
            
        return formatted_matches 