import streamlit as st
import fitz  # PyMuPDF
import io

def hex_to_rgb(hex_color):
    """แปลงสีจากโค้ด Hex (เช่น #FFFF00) เป็น RGB ค่า 0-1 สำหรับ PyMuPDF"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def highlight_pdf(file_bytes, search_text, color_rgb):
    """ฟังก์ชันค้นหาคำและไฮไลต์สีใน PDF"""
    # เปิดไฟล์ PDF จาก Bytes
    pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    
    # วนลูปตรวจสอบทุกหน้าใน PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        # ค้นหาตำแหน่งของคำที่ต้องการ
        text_instances = page.search_for(search_text)
        
        # วนลูปไฮไลต์ทุกจุดที่เจอคำนั้น
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors(stroke=color_rgb) # ตั้งค่าสี
            highlight.update()
            
    # บันทึกไฟล์ที่ไฮไลต์แล้วกลับเป็น Bytes
    output_pdf = io.BytesIO()
    pdf_document.save(output_pdf)
    pdf_document.close()
    
    return output_pdf.getvalue()

# ==========================================
# ส่วนของการสร้างหน้าจอ UI ด้วย Streamlit
# ==========================================
st.set_page_config(page_title="โปรแกรมไฮไลต์ PDF", page_icon="🖍️")
st.title("🖍️ โปรแกรมไฮไลต์ข้อความใน PDF")
st.write("อัปโหลดไฟล์ PDF ของคุณ พิมพ์ข้อความที่ต้องการเน้น เลือกสี และกดดาวน์โหลดได้เลย")

# 1. กล่องอัปโหลดไฟล์
uploaded_file = st.file_uploader("📂 เลือกไฟล์ PDF ที่ต้องการ", type="pdf")

if uploaded_file is not None:
    # 2. กล่องรับข้อความที่ต้องการค้นหา
    search_text = st.text_input("🔍 พิมพ์ข้อความที่ต้องการไฮไลต์", placeholder="เช่น ๑๙,๐๐๐,๐๐๐ บาท")
    
    # 3. ตัวเลือกสี (ค่าเริ่มต้นคือสีเหลือง)
    color_hex = st.color_picker("🎨 เลือกสีไฮไลต์", "#FFFF00")
    
    if st.button("✨ ทำการไฮไลต์ข้อความ"):
        if search_text.strip() == "":
            st.warning("⚠️ กรุณาพิมพ์ข้อความที่ต้องการค้นหาก่อนครับ")
        else:
            with st.spinner("กำลังประมวลผลไฟล์..."):
                try:
                    # อ่านไฟล์และแปลงสี
                    pdf_bytes = uploaded_file.read()
                    color_rgb = hex_to_rgb(color_hex)
                    
                    # เรียกใช้ฟังก์ชันไฮไลต์
                    highlighted_pdf_bytes = highlight_pdf(pdf_bytes, search_text, color_rgb)
                    
                    st.success("✅ ไฮไลต์สำเร็จเรียบร้อยแล้ว!")
                    
                    # 4. ปุ่มดาวน์โหลดไฟล์ที่ทำเสร็จแล้ว
                    st.download_button(
                        label="📥 ดาวน์โหลดไฟล์ PDF ที่ไฮไลต์แล้ว",
                        data=highlighted_pdf_bytes,
                        file_name=f"highlighted_{uploaded_file.name}",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
