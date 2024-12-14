from flask import Flask, request, jsonify,send_from_directory

from flask_cors import CORS
from elasticsearch import Elasticsearch

import pandas as pd
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app)  # Cho phép kết nối từ frontend
es = Elasticsearch(
    ['http://localhost:9200'],
    request_timeout=1000  # Tăng thời gian timeout lên 30 giây
)
INDEX_NAME = "movies"  # Tên index trong Elasticsearch

# Load mô hình SentenceTransformer để tạo embeddings``
model = SentenceTransformer("all-MiniLM-L6-v2")

# Tạo index trong Elasticsearch
def create_index():
    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists.")
        return
    try:
        es.indices.create(index=INDEX_NAME, body={
            "mappings": {
                "properties": {
                    "release_year": {"type": "integer"},
                    "title": {"type": "text"},
                    "origin_ethnicity": {"type": "text"},
                    "director": {"type": "text"},
                    "plot": {"type": "text"},
                    "genre": {"type": "text"},
                    "wiki_page": {"type": "text", "index": False},
                    "embedding": {"type": "dense_vector", "dims": 384}
                }
            }
        })
        print(f"Index '{INDEX_NAME}' created.")
    except Exception as e:
        print(f"Error creating index: {e}")


# Nạp dữ liệu vào Elasticsearch
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    for idx, row in df.iterrows():
        try:
            embedding = model.encode(row["Plot"].strip()).tolist() if pd.notna(row["Plot"]) else None
            document = {
                "release_year": int(row["Release Year"]) if pd.notna(row["Release Year"]) else None,
                "title": row["Title"],
                "origin_ethnicity": row["Origin/Ethnicity"],
                "director": row["Director"],
                "plot": row["Plot"],
                "genre": row["Genre"],
                "wiki_page": row["Wiki Page"],
                "embedding": embedding
            }
            es.index(index=INDEX_NAME, id=idx, body=document)
        except Exception as e:
            print(f"Error at row {idx}: {e}")

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


@app.route("/search", methods=["GET"])
# def search():
#     query = request.args.get("q")
#     # print(query)
#     if not query:
#         return jsonify({"error": "Query parameter 'q' is required"}), 400

#     try:
#         # Xây dựng truy vấn Elasticsearch
#         body = {
#             "query": {
#                 "match": {
#                     "title": query
#                 }
#             }
#         }
#         print("Query Body:", body)

#         # Thực hiện tìm kiếm
#         res = es.search(index=INDEX_NAME, body=body)

#         # print(f"Elasticsearch Response: {res}")

#         hits = res["hits"]["hits"]

#         # Trả kết quả
#         results = [
#             {
#                 "rank": idx + 1,
#                 "score": hit["_score"],
#                 **hit["_source"]
#             }
#             for idx, hit in enumerate(hits)
#         ]
#         print(results)
#         return jsonify(results)

#     except Exception as e:
#         print("Query Body:", body)
#         print(f"Error during search: {e}")
#         return jsonify({"error": str(e)}), 500

def search():
    # Lấy các tham số query và field từ URL
    field = request.args.get("field")  # Trường để tìm kiếm
    query = request.args.get("q")      # Giá trị tìm kiếm

    if not field or not query:
        return jsonify({"error": "Both 'field' and 'q' parameters are required"}), 400

    try:
        # Danh sách các trường hợp lệ
        valid_fields = ["title", "director", "genre", "plot"]

        # Kiểm tra xem trường có hợp lệ không
        if field not in valid_fields:
            return jsonify({"error": f"Invalid field: {field}. Valid fields are {', '.join(valid_fields)}"}), 400

        # Xây dựng truy vấn Elasticsearch
        body = {
            "query": {
                "match": {
                    field: query  # Truy vấn theo trường được chọn
                }
            }
        }
        print("Query Body:", body)

        # Thực hiện tìm kiếm
        res = es.search(index=INDEX_NAME, body=body)
        hits = res["hits"]["hits"]

        # Trả kết quả
        results = [
            {
                "rank": idx + 1,
                "score": hit["_score"],
                **hit["_source"]
            }
            for idx, hit in enumerate(hits)
        ]
        print(results)
        return jsonify(results)

    except Exception as e:
        print("Query Body:", body)
        print(f"Error during search: {e}")
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    create_index()
    #load_data("data.csv")  # Load dữ liệu từ dataset
    app.run(host="0.0.0.0", port=5000)
