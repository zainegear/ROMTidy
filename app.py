# -*- coding: utf-8 -*-
import streamlit as st
import re
import os
import zipfile
import io

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ROMTidy - Retro ROM Manager",
    page_icon="🕹️",
    layout="wide"
)

# ตกแต่ง UI คลีนๆ สบายตา
st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🕹️ ROMTidy Web Edition</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">ระบบจัดระเบียบชื่อไฟล์ ROM อัตโนมัติ ลบแท็กขยะ จัดช่องว่าง และรักษารหัสภาษาไทย/อังกฤษ</p>', unsafe_allow_html=True)

# ช่องอัปโหลดไฟล์ ROM
uploaded_files = st.file_uploader(
    "ลากไฟล์ ROM มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์ (รองรับหลายไฟล์พร้อมกัน)",
    accept_multiple_files=True,
    type=['nes', 'gb', 'gbc', 'sfc', 'smc', 'bin', 'md', 'pce', 'gba', 'nds', 'z64', 'n64', 'v64', 'gdi', 'zip', 'cue', 'chd', 'iso', 'cso', 'rvz']
)

def clean_rom_name(filename):
    name, ext = os.path.splitext(filename)
    
    # 1. รักษาสถานะภาษาเดิม [T-En] หรือ [T-Th]
    translation_tag = ""
    if re.search(r'\[T-En', name, flags=re.IGNORECASE):
        translation_tag = "[T-En]"
    elif re.search(r'\[T-Th', name, flags=re.IGNORECASE):
        translation_tag = "[T-Th]"

    # 2. ตัดเครดิตการแปลยาวๆ ออก
    clean_name = re.sub(r'\s*\[T-[A-Za-z0-9\s\-\.]+\]', '', name, flags=re.IGNORECASE)
    
    # 3. ลบแท็กขยะ [n], [i], [!] ออกอย่างหมดจด
    clean_name = re.sub(r'\s*\[[a-zA-Z!]\]', '', clean_name)
    
    # 4. จัดการช่องว่างและขีดล่าง
    clean_name = clean_name.replace("_", " ").strip()
    clean_name = re.sub(r'\s+', ' ', clean_name)
    
    # 5. คืนค่าป้ายภาษาเดิม หรือเติม (USA) ถ้าไม่มีโซน
    if translation_tag:
        clean_name = f"{clean_name} {translation_tag}"
    else:
        if not any(region in clean_name for region in ["(USA)", "(Japan)", "(Europe)", "(Asia)"]):
            clean_name = f"{clean_name} (USA)"
        
    return f"{clean_name}{ext}"

if uploaded_files:
    st.divider()
    st.subheader("📋 ตรวจสอบรายการไฟล์ (Preview)")
    
    preview_data = []
    processed_files = []
    
    for file in uploaded_files:
        original_name = file.name
        new_name = clean_rom_name(original_name)
        file_size = f"{file.size / (1024*1024):.2f} MB"
        preview_data.append({
            "ชื่อไฟล์เดิม": original_name,
            "ชื่อไฟล์หลังจัดระเบียบ": new_name,
            "ขนาด": file_size
        })
        processed_files.append((new_name, file.getvalue()))

    # แสดงตารางเปรียบเทียบ
    st.dataframe(preview_data, use_container_width=True, hide_index=True)

    # สร้างไฟล์ ZIP สำหรับดาวน์โหลดรวม
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for new_name, file_bytes in processed_files:
            zip_file.writestr(new_name, file_bytes)
    
    zip_buffer.seek(0)

    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"พร้อมดาวน์โหลดไฟล์ที่จัดระเบียบแล้วทั้งหมด {len(processed_files)} ไฟล์")
    with col2:
        st.download_button(
            label="📦 ดาวน์โหลดไฟล์ทั้งหมด (ZIP)",
            data=zip_buffer,
            file_name="ROMTidy_Cleaned.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
else:
    st.info("💡 เริ่มต้นใช้งานโดยการอัปโหลดไฟล์ ROM เข้ามาในระบบด้านบน")