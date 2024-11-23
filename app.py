import streamlit as st
from pydantic import BaseModel
import json
from docling.document_converter import DocumentConverter
from models import ExtractA, ExtractB, ExtractC, ExtractD
from utils import clean_text, chunk_by_token
import tempfile
from docx import Document


def export_to_word(questions):
    """
    Xuất danh sách câu hỏi ra file Word và trả về nội dung file.
    """
    doc = Document()
    doc.add_heading("Danh sách câu hỏi", level=1)
    
    for idx, quiz in enumerate(questions, start=1):
        doc.add_heading(f"Câu {idx} ({quiz['level']}):", level=2)
        doc.add_paragraph(quiz["question"])
        doc.add_paragraph("Đáp án:")
        for i, choice in enumerate(quiz["choices"], start=1):
            doc.add_paragraph(f"{i}. {choice}")
        doc.add_paragraph(f"Đáp án đúng: {quiz['answer']}")
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_file.name)
    temp_file.seek(0)  # Đặt con trỏ về đầu file
    return temp_file


# Streamlit UI
st.title("Trích xuất câu hỏi từ tài liệu")

# Tải file lên
uploaded_file = st.file_uploader("Tải lên một file tài liệu (.docx)", type=["docx"])

if uploaded_file is not None:
    with st.spinner("Đang xử lý tệp..."):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        # Sử dụng DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(temp_file_path)
        text = result.document.export_to_markdown()

    # Chia văn bản thành các chunk
    chunks = chunk_by_token(text, max_len=1000)
    total_chunks = len(chunks)

    # Hiển thị slider để chọn các chunk
    st.write("### Điều chỉnh phạm vi hiển thị các chunk:")
    start, end = st.slider(
        "Chọn chỉ mục chunk bắt đầu và kết thúc",
        min_value=0,
        max_value=total_chunks - 1,
        value=(0, min(5, total_chunks - 1)),
        step=1
    )

    # Hiển thị chunk trong phạm vi được chọn
    st.write(f"### Hiển thị chunk từ {start} đến {end} (tổng: {end - start + 1} chunk):")
    selected_chunks = chunks[start:end + 1]
    num_selected_chunks = len(selected_chunks)

    # Cảnh báo hoặc báo lỗi nếu chọn quá nhiều chunk
    if num_selected_chunks > 5:
        st.error("Bạn cho quá nhiều dữ liệu input. Vui lòng giảm số lượng chunk.")
    elif num_selected_chunks > 3:
        st.warning(
            "Số lượng chunk bạn chọn khá lớn. Việc xử lý có thể mất nhiều thời gian và tốn nhiều chi phí hơn."
        )

    st.text_area("Kết quả", "\n\n".join(selected_chunks), height=300)

    # Chọn mức độ câu hỏi cần trích xuất
    extraction_levels = {
        "Dễ": ExtractA,
        "Thông hiểu": ExtractB,
        "Vận dụng": ExtractC,
        "Vận dụng cao": ExtractD
    }
    selected_levels = st.multiselect(
        "Chọn mức độ câu hỏi cần trích xuất",
        options=list(extraction_levels.keys()),
        default=["Dễ", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
    )

    if st.button("Trích xuất câu hỏi"):
        # Kiểm tra lại số lượng chunk được chọn trước khi xử lý
        if num_selected_chunks > 5:
            st.error("Không thể xử lý vì số lượng chunk quá lớn. Vui lòng giảm số lượng chunk.")
        else:
            with st.spinner("Đang trích xuất câu hỏi..."):
                # Chỉ trích xuất từ các chunk được chọn
                all_results = []

                for level in selected_levels:
                    extractor_class = extraction_levels[level]
                    extractor = extractor_class()
                    result = extractor.run(" ".join(selected_chunks))
                    all_results.extend(result["quizes"])

                # Hiển thị kết quả
                st.write("### Câu hỏi được trích xuất:")
                for quiz in all_results:
                    st.write(f"#### Câu hỏi ({quiz['level']}):")
                    st.write(quiz["question"])
                    st.write("**Đáp án:**")
                    for i, choice in enumerate(quiz["choices"], 1):
                        st.write(f"{i}. {choice}")
                    st.write(f"**Đáp án đúng:** {quiz['answer']}")

                # Nút xuất ra Word
                temp_file = export_to_word(all_results)
                with open(temp_file.name, "rb") as f:
                    st.download_button(
                        label="Tải xuống file Word",
                        data=f,
                        file_name="questions.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
