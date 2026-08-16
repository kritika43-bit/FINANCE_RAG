import os
import pdfplumber

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def simple_chunk(text: str, chunk_size: int = 1000, overlap: int = 150):
    chunks = []
    if not text:
        return chunks
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        if end == length:
            break
        start = max(0, end - overlap)
    return chunks


def main():
    pdfs = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]
    if not pdfs:
        print("No PDF files found in data/")
        return

    total_pages = 0
    total_chunks = 0
    for p in pdfs:
        path = os.path.join(DATA_DIR, p)
        with pdfplumber.open(path) as pdf:
            pages = pdf.pages
            print(f"{p}: {len(pages)} pages")
            total_pages += len(pages)
            for i, page in enumerate(pages, start=1):
                text = page.extract_text() or ""
                if not text.strip():
                    continue
                chunks = simple_chunk(text, chunk_size=1000, overlap=150)
                total_chunks += len(chunks)

    print(f"Total pages: {total_pages}")
    print(f"Total chunks after splitting: {total_chunks}")


if __name__ == '__main__':
    main()
