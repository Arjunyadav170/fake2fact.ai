from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from newspaper import Article
# from transformers import pipeline
import psycopg2

app = Flask(__name__)


#GEMINI API use
genai.configure(api_key="AIzaSyBHsBskArnL0GuPaPQgWuJYKSROCDl9VqQ")

# from transformers import BartForConditionalGeneration, BartTokenizer
# import torch
#
# # Load PyTorch-based summarization model manually
# model_name = "facebook/bart-large-cnn"
# tokenizer = BartTokenizer.from_pretrained(model_name)
# local_model = BartForConditionalGeneration.from_pretrained(model_name)


# for embedding user text for similarity search
model = SentenceTransformer('all-MiniLM-L6-v2')


def semantic_search(embedding):
    # postgres connecting
    conn = psycopg2.connect(
        dbname="fake2fact",
        user="postgres",
        password="1084",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    # cosine similarity
    cur.execute("""
         SELECT id, title, link, source, published,summary, 
                1 - (embedding <=> %s::vector) AS similarity
         FROM all_news_cleaned
         ORDER BY embedding <=> %s::vector
         LIMIT 2;
     """, (embedding, embedding))

    results = cur.fetchall()
    # return metadata
    response_out = [
        {
            "id": r[0],
            "title": r[1],
            "link": r[2],
            "source": r[3],
            "published": r[4],
            "summary": r[5],
            "similarity": r[6]
        }
        for r in results
    ]
    cur.close()
    conn.close()
    return response_out


def extract_link_text(response):
    articles_text_out = []

    for item in response:
        url = item.get("link")  # safely get link
        if not url:
            continue

        try:
            article = Article(url)
            article.download()
            article.parse()
            articles_text_out.append(article.text)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            articles_text_out.append("")  # keep index alignment

    return articles_text_out


def summarize_articles(response, articles_text):
    summaries = []

    for i, article_text in enumerate(articles_text):
        url = response[i].get("link", "No Link Provided")
        title = response[i].get("title", "Untitled Article")
        source = response[i].get("source", "Source not available")
        published = response[i].get("published", "Published date not mentioned")
        short_summary = response[i].get("summary", "No short summary provided")

        if not article_text.strip():
            summaries.append({
                "title": title,
                "link": url,
                "source": source,
                "published": published,
                "short_summary": short_summary,
                "final_summary": "No text extracted."
            })
            continue

        try:
            #  gemini summary
            prompt = f"""
            Summarize and explain this news article in a factual, concise way.
            Include context, source reliability, and main key points.

            Article title: {title}
            Article text: {article_text[:800]}  # limit for safety
            """

            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            gemini_response = model.generate_content(prompt)

            summary_text = gemini_response.text.strip()
            print(f" Gemini summarized: {title}")

        except Exception as e:
            #  fallback
            print(f" Gemini failed for '{title}' → using local summarizer. Error: {e}")
            try:
                # inputs = tokenizer([article_text], max_length=1024, return_tensors="pt", truncation=True)
                # summary_ids = local_model.generate(
                #     inputs["input_ids"],
                #     max_length=150,
                #     min_length=50,
                #     length_penalty=2.0,
                #     num_beams=4,
                #     early_stopping=True
                # )
                # summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                summary_text=article_text[:800]

            except Exception as local_error:
                print(f" Local summarizer failed: {local_error}")
                summary_text = "Unable to summarize due to technical error."

        #  Combine everything into final summary dictionary
        summaries.append({
            "title": title,
            "link": url,
            "source": source,
            "published": published,
            "short_summary": short_summary,
            "final_summary": summary_text
        })

    return summaries



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# user input data fetching
@app.route('/claim_checking', methods=['POST'])
def claim_checking():
    data=request.get_json()
    input_type = data.get('input_type')
    claim = data.get('claim')




    if input_type == 'text_button':
        # process text claim

        user_embedding = model.encode(claim).tolist()
        response_=semantic_search(user_embedding)
        article_text_=extract_link_text(response_)
        final_result=summarize_articles(response_,article_text_)


        return jsonify({'result': final_result})
    elif input_type == 'url_button':
        # process URL claim (future feature)
        result = f"Checked URL: {claim}"
    else:
        result = "Unknown input type"

    return jsonify({'result': result})










if __name__ == '__main__':
    app.run(debug=True)