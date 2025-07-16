import pandas as pd
from typing import List
from agents.ollama_client import OllamaClient
import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector

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
        if pgvector_dsn:
            self._init_pgvector()

    def _init_pgvector(self):
        self.conn = psycopg2.connect(self.pgvector_dsn)
        register_vector(self.conn)
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS merchant_embeddings (
                    merchant_id TEXT PRIMARY KEY,
                    embedding vector(384)
                )
            """)
            # Insert or update embeddings for all merchants
            for _, row in self.df.iterrows():
                emb = get_embedding(row['message']).tolist()
                cur.execute("""
                    INSERT INTO merchant_embeddings (merchant_id, embedding)
                    VALUES (%s, %s)
                    ON CONFLICT (merchant_id) DO UPDATE SET embedding = EXCLUDED.embedding
                """, (row['merchant_id'], emb))
            self.conn.commit()

    def get_merchant_name(self, merchant_id: str) -> str:
        row = self.df[self.df['merchant_id'] == merchant_id]
        if not row.empty:
            return row.iloc[0].get('mcc_description', merchant_id)
        return merchant_id

    def find_matches(self, user_id: str, message: str) -> List[str]:
        user_row = self.df[self.df['merchant_id'] == user_id]
        if user_row.empty:
            return []
        city = user_row.iloc[0]['city']
        mcc_code = user_row.iloc[0]['mcc_code']
        user_profile = f"Merchant ID: {user_id}, City: {city}, MCC: {mcc_code}, Message: {message}"
        candidates = self.df[(self.df['city'] == city) & (self.df['merchant_id'] != user_id)]
        candidate_profiles = [
            f"Merchant ID: {row['merchant_id']}, City: {row['city']}, MCC: {row['mcc_code']}, Message: {row['message']}"
            for _, row in candidates.iterrows()
        ]
        if self.pgvector_dsn and not user_row.empty:
            # Semantic search with PGVector
            user_emb = get_embedding(message)
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT merchant_id
                    FROM merchant_embeddings
                    WHERE merchant_id != %s
                    ORDER BY embedding <-> %s
                    LIMIT 5
                """, (user_id, user_emb.tolist()))
                match_ids = [row[0] for row in cur.fetchall()]
            match_names = [self.get_merchant_name(mid) for mid in match_ids]
            return match_names
        if not candidate_profiles:
            return []
        prompt = (
            f"{SYSTEM_PROMPT}\nUser: {user_profile}\nCandidates:\n" + "\n".join(candidate_profiles) + "\nMatches:"
        )
        result = self.llm.generate(prompt)
        matches = [m.strip() for m in result.split(",") if m.strip() in candidates['merchant_id'].values]
        match_names = [self.get_merchant_name(mid) for mid in matches[:5]]
        return match_names 