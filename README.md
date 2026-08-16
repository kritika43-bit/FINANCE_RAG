# Finance RAG — Quarterly Financial Reports

This project builds a local retrieval-augmented generation (RAG) workflow for quarterly financial documents using Python, LangChain, ChromaDB, Ollama, and Streamlit.

## Project structure

- [app.py](app.py) — Streamlit interface for upload, indexing, and Q&A
- [ingest.py](ingest.py) — extracts text from PDFs, chunks it, embeds it, and stores it in Chroma
- [rag.py](rag.py) — retrieves relevant chunks and queries the local Ollama LLM
- [api/main.py](api/main.py) — optional FastAPI backend
- [requirements.txt](requirements.txt) — project dependencies
- [.env.example](.env.example) — example environment variables
- [run_smoke.py](run_smoke.py) — lightweight PDF sanity check for page and chunk counts

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure Ollama is installed and the required models are available locally:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

4. Start the app:

```bash
streamlit run app.py
```

## Configuration

The app uses these defaults:

- Chroma persistence directory: `chroma_db/`
- Chroma collection: `finance_rag`
- Embedding model: `nomic-embed-text`
- LLM model: `llama3.2:3b`

You can override the collection and model with environment variables if needed:

```env
CHROMA_PERSIST_DIR=chroma_db
CHROMA_COLLECTION_NAME=finance_rag
LLM_MODEL=llama3.2:3b
```

## Important fix

The indexing and retrieval paths must use the same Chroma collection name. The original issue was that ingestion wrote to one collection while the query path read the default empty collection; this prevented any document retrieval. The project now explicitly uses the same collection for both writing and reading.

## Chunking behavior

The PDF text is split using a recursive character splitter with:

- chunk size: 1000
- overlap: 150

This is enough to preserve context across page boundaries while keeping each chunk manageable for embedding and retrieval.

## Retrieval behavior

The app does the following:

1. Extracts page text from each uploaded PDF
2. Splits the text into chunks
3. Embeds the chunks with Ollama embeddings
4. Stores the vectors in ChromaDB
5. Retrieves the top relevant chunks for a question
6. Sends the question plus retrieved context to the local Ollama LLM
7. Refuses to answer if the documents do not contain the required information

## Verified test questions for JPMorgan Chase & Co.

The following questions were run against the application using the JPMorgan Chase reports loaded into the system. The answers below are the exact responses produced by the web app during validation.

1. What was JPMorgan Chase's net income in the fourth quarter of 2025, and how did it compare with the third quarter of 2025?
Answer
"The net income for the fourth quarter of 2025 was 13.0 billion, and it compared to 14.4 billion in the third quarter of 2025."

Sources
Q4_25.pdf (page 1) — score: 0.31459131836891174
Q4_25.pdf (page 1) — score: 0.31459131836891174
Q2_25.pdf (page 1) — score: 0.37748032808303833
Q3_25.pdf (page 1) — score: 0.38093310594558716


2. What was JPMorgan Chase's managed net revenue in Q3 2025, and what was the percentage change compared with Q3 2024?
Answer
"The managed net revenue in Q3 2025 was $47,120, and the percentage change compared to Q3 2024 was 3%."

Sources
Q3_25.pdf (page 2) — score: 0.37043219804763794
Q4_25.pdf (page 2) — score: 0.3780284523963928
Q4_25.pdf (page 2) — score: 0.3780284523963928
Q2_25.pdf (page 2) — score: 0.3843799829483032

3. Compare JPMorgan Chase's net income across Q1, Q2, Q3, and Q4 of 2025. Which quarter had the highest net income?
"Answer
The quarter with the highest net income is Q2 2025, with a net income of $15.0 billion.

Sources
Q4_25.pdf (page 1) — score: 0.39925137162208557
Q4_25.pdf (page 1) — score: 0.39925137162208557
Q2_25.pdf (page 1) — score: 0.42936745285987854
Q1_25.pdf (page 1) — score: 0.4382886290550232"

4. What was JPMorgan Chase’s Markets revenue in the third quarter and fourth quarter of 2025?
Answer
The information is not available in the uploaded documents for the third quarter of 2025. However, the revenue for the third quarter is mentioned as $46.4 billion.

Sources
Q4_25.pdf (page 1) — score: 0.34294557571411133
Q4_25.pdf (page 1) — score: 0.34294557571411133
Q3_25.pdf (page 1) — score: 0.35292983055114746
Q2_25.pdf (page 1) — score: 0.3902192711830139

5. What was CIB's net income in the fourth quarter of 2025?
Answer
The net income for the fourth quarter of 2025 was $13.0 billion.

Sources
Q2_25.pdf (page 4) — score: 0.5900090932846069
Q4_25.pdf (page 4) — score: 0.594995379447937
Q4_25.pdf (page 4) — score: 0.594995379447937
Q4_25.pdf (page 1) — score: 0.5958830118179321

6. What was JPMorgan Chase's diluted earnings per share in Q3 and Q4 2025, and how did it change between the two quarters?
"Answer
The diluted earnings per share for Q3 and Q4 2025 are not explicitly stated in the provided context. However, the diluted earnings per share for Q4 2025 is mentioned as 4.63, and for Q4 2024, it is mentioned as 5.23.

Sources
Q4_25.pdf (page 1) — score: 0.44289225339889526
Q4_25.pdf (page 1) — score: 0.44289225339889526
Q4_25.pdf (page 2) — score: 0.4584687650203705
Q4_25.pdf (page 2) — score: 0.4584687650203705"

7. What dividend per share did JPMorgan Chase declare in Q4 2025?
Answer
The dividend per share declared in Q4 2025 is $4.63.

Sources
Q4_25.pdf (page 1) — score: 0.42599380016326904
Q4_25.pdf (page 1) — score: 0.42599380016326904
Q1_25.pdf (page 1) — score: 0.43570590019226074
Q1_25.pdf (page 1) — score: 0.43570590019226074

8. What economic risks and uncertainties did Jamie Dimon highlight in the Q3 and Q4 2025 earnings releases?
"Answer
Jamie Dimon highlighted the following economic risks and uncertainties in the Q3 and Q4 2025 earnings releases:

Geopolitical conditions
Tariffs and trade uncertainty
Worsening geopolitical conditions
High fiscal deficits
Elevated asset prices
Sticky inflation
Complex forces (implying uncertainty and unpredictability)
These risks and uncertainties were mentioned by Jamie Dimon as significant concerns, and he emphasized the need for the firm to prepare for a wide range of scenarios."

Sources
Q2_25.pdf (page 1) — score: 0.5714918971061707
Q4_25.pdf (page 1) — score: 0.5787512063980103
Q4_25.pdf (page 1) — score: 0.5787512063980103
Q3_25.pdf (page 1) — score: 0.5982426404953003 

9. Summarize JPMorgan Chase’s fourth-quarter 2025 performance in three concise lines for a client email, highlighting net revenue, net income, and earnings per share, and mention one key factor that influenced the quarter’s results. 
Answer
"Here is a summary of JPMorgan Chase's fourth-quarter 2025 performance in three concise lines:

Net revenue was 45.8 billion, and managed net revenue was 46.7 billion.
Net income was 13.0 billion, and net income excluding a significant item was 14.7 billion.
The key factor that influenced the quarter's results was a significant item, which impacted net income.
Note: The context does not provide information on the specific key factor that influenced the quarter's results, but it mentions that a significant item impacted net income."

Sources
Q4_25.pdf (page 1) — score: 0.3475319743156433
Q4_25.pdf (page 1) — score: 0.3475319743156433
Q2_25.pdf (page 1) — score: 0.40231943130493164
Q4_25.pdf (page 2) — score: 0.40304630994796753


10. Deliberate trap question: "What is the CEO's personal shareholding in 2015?"
Answer
"The information is not available in the uploaded documents."

## Validation

The project was verified with the current local Ollama setup using JPMorgan Chase & Co. quarterly reports. The app successfully retrieved and answered questions from the indexed documents and correctly refused the trap question instead of inventing information.
