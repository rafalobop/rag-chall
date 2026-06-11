import chromadb

client = chromadb.EphemeralClient()
collection = client.create_collection("test_coll")

collection.add(
    ids=["1"],
    documents=["Ficción Espacial: En el planeta Zenthoria, Zara descubrió el artefacto místico."],
    metadatas=[{"source": "Ficción Espacial"}]
)

print("Count:", collection.count())
res = collection.query(query_texts=["Zara"], n_results=1)
print("Query results:", res)
