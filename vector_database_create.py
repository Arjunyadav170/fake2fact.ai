import psycopg2
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="fake2fact",
    user="postgres",
    password="1084",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Select rows where embedding is not yet generated
cur.execute("SELECT id, clean_text FROM all_news_cleaned WHERE embedding IS NULL;")
rows = cur.fetchall()

# Load the sentence transformer model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to get embeddings
def get_embedding(text):
    try:
        embedding = model.encode(text)
        return embedding.tolist()  # convert to list for PostgreSQL
    except Exception as e:
        print(" Error generating embedding:", e)
        return None

# Generate and save embeddings
for row in tqdm(rows, desc="Generating embeddings"):
    id_, text = row
    if not text:
        continue

    embedding = get_embedding(text)
    if embedding is not None:
        cur.execute(
            "UPDATE all_news_cleaned SET embedding = %s WHERE id = %s;",
            (embedding, id_)
        )


conn.commit()
cur.close()
conn.close()

print(" Embeddings successfully added to all_news_cleaned table!")
