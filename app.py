import io
import os
import fitz
import streamlit as st

st.set_page_config(page_title="ค้นหาเกียรติบัตร", page_icon="📜")
st.title("📜 ระบบค้นหาและดาวน์โหลดเกียรติบัตร")

PDF_PATH = "certificates.pdf"

if not os.path.exists(PDF_PATH):
    st.error("ไม่พบไฟล์ certificates.pdf ในระบบ")
    st.stop()

search_name = st.text_input("กรอกชื่อ-นามสกุล ที่ต้องการค้นหา:")

if st.button("ค้นหาเกียรติบัตร"):
    if not search_name.strip():
        st.warning("กรุณากรอกชื่อก่อนกดค้นหา")
    else:
        doc = fitz.open(PDF_PATH)
        clean_search = search_name.replace(" ", "").strip()
        matched_pages = []

        for page_index in range(len(doc)):
            page_text = doc[page_index].get_text().replace(" ", "").strip()
            if clean_search in page_text:
                matched_pages.append(page_index)

        if matched_pages:
            st.success(f"พบเกียรติบัตรของคุณทั้งหมด {len(matched_pages)} หน้า")

            out_doc = fitz.open()
            for p in matched_pages:
                out_doc.insert_pdf(doc, from_page=p, to_page=p)

            pdf_buffer = io.BytesIO()
            out_doc.save(pdf_buffer)
            out_doc.close()

            st.download_button(
                label="⬇️ คลิกที่นี่เพื่อดาวน์โหลดเกียรติบัตร",
                data=pdf_buffer.getvalue(),
                file_name=f"เกียรติบัตร_{search_name.strip()}.pdf",
                mime="application/pdf",
            )
        else:
            st.error(f"ไม่พบชื่อ '{search_name}' โปรดตรวจตัวสะกด")

        doc.close()