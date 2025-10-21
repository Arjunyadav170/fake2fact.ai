import psycopg2
import re
conn=psycopg2.connect(
    dbname="fake2fact",
    user="postgres",
    password="1084",
    host="localhost",
    port="5432"
    )
cur=conn.cursor()

cur.execute("SELECT title, link, source, published,summary FROM all_news;")
predata=cur.fetchall()

# Preprocessing function
def clean_html(text):
    text = re.sub(r'<[^>]+>', ' ', text)  # html tags remove 
    return text.lower().strip()

for data in predata:
    title, link, source, published,summary =data
    clean_text=clean_html((title or "")+ " "+(summary or ""))
    cur.execute("""
        INSERT INTO all_news_cleaned (title, link, source, published,summary , clean_text)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING
    """, (title, link, source, published,summary , clean_text))
    
conn.commit()
cur.close()
conn.close()
print("✅ Articles stored in PostgreSQL")    
    