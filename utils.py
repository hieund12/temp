
# Định nghĩa các hàm phụ trợ
def clean_text(text):
    text = text.replace("\n", " ")
    text = text.replace("-", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split(" "))
    return text.strip()

def chunk_by_token(text, max_len=1000):
    words = clean_text(text).split(" ")
    chunks = []
    current_chunk = []
    current_len = 0
    for word in words:
        if current_len + 1 > max_len:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(word)
        current_len += 1
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks