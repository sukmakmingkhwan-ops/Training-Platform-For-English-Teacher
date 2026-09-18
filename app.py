import io
import os
import fitz  # PyMuPDF
import streamlit as st

st.set_page_config(
    page_title="ค้นหาเกียรติบัตร", page_icon="📜", layout="centered"
)
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

        # ค้นหาข้อความทุกหน้า
        for page_index in range(len(doc)):
            page_text = doc[page_index].get_text().replace(" ", "").strip()
            if clean_search in page_text:
                matched_pages.append(page_index)

        if matched_pages:
            st.success(
                f"พบเกียรติบัตรของคุณทั้งหมด {len(matched_pages)} รายการ"
            )

            # แสดงภาพตัวอย่างและปุ่มดาวน์โหลดแยกตามแต่ละหน้าที่พบ
            for idx, p in enumerate(matched_pages, start=1):
                page = doc[p]

                # 1. แปลงหน้า PDF เป็นรูปภาพเพื่อ Preview
                pix = page.get_pixmap(dpi=150)  # ความคมชัด 150 dpi
                img_bytes = pix.tobytes("png")

                st.markdown(f"### 📄 เกียรติบัตรใบที่ {idx}")
                st.image(img_bytes, caption=f"หน้า {p + 1}", use_container_width=True)

                # 2. สร้างไฟล์ PDF เฉพาะใบนี้สำหรับดาวน์โหลด
                single_doc = fitz.open()
                single_doc.insert_pdf(doc, from_page=p, to_page=p)

                pdf_buffer = io.BytesIO()
                single_doc.save(pdf_buffer)
                single_doc.close()

                # ปุ่มดาวน์โหลดเฉพาะใบ
                st.download_button(
                    label=f"⬇️ ดาวน์โหลดเกียรติบัตรใบที่ {idx} (.pdf)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"เกียรติบัตร_{search_name.strip()}_ใบที่{idx}.pdf",
                    mime="application/pdf",
                    key=f"download_{p}",
                )
                st.divider()

            # กรณีพบมากกว่า 1 ใบ: มีปุ่มให้โหลดรวมทุกใบพร้อมกันทีเดียว
            if len(matched_pages) > 1:
                all_doc = fitz.open()
                for p in matched_pages:
                    all_doc.insert_pdf(doc, from_page=p, to_page=p)

                all_buffer = io.BytesIO()
                all_doc.save(all_buffer)
                all_doc.close()

                st.download_button(
                    label="📦 ดาวน์โหลดเกียรติบัตรทั้งหมดรวมกัน (PDF รวม)",
                    data=all_buffer.getvalue(),
                    file_name=f"เกียรติบัตร_{search_name.strip()}_ทั้งหมด.pdf",
                    mime="application/pdf",
                    key="download_all",
                )
        else:
            st.error(f"ไม่พบชื่อ '{search_name}' โปรดตรวจสอบตัวสะกด")

        doc.close()
