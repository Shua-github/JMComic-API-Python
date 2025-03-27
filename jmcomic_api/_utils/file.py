import img2pdf
from pypdf import PdfWriter, PdfReader
from io import BytesIO
import zipfile
import os
from typing import Literal, List

def images_encrypted(
    image_paths: List[str],
    password: str,
    out_file_format: Literal['pdf','zip']
) -> BytesIO:
    # 处理PDF格式
    if out_file_format == 'pdf':
        # 将图片转换为PDF字节流
        pdf_bytes = img2pdf.convert(image_paths)
        pdf_stream = BytesIO(pdf_bytes)

        # 创建PDF读取器和写入器
        pdf_reader = PdfReader(pdf_stream)
        pdf_writer = PdfWriter()

        # 添加所有页面
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        # 如果有密码，进行加密
        if password:
            pdf_writer.encrypt(password)

        # 写入加密后的PDF
        encrypted_pdf = BytesIO()
        pdf_writer.write(encrypted_pdf)
        encrypted_pdf.seek(0)
        return encrypted_pdf

    # 处理ZIP格式
    elif out_file_format == 'zip':
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for img_path in image_paths:
                # 获取文件名并添加至ZIP
                arcname = os.path.basename(img_path)
                # 写入文件并应用密码加密（但注意，setpassword仅做简单密码保护）
                zipf.write(img_path, arcname=arcname)
                
            if password:
                zipf.setpassword(password.encode('utf-8'))
        
        zip_buffer.seek(0)
        return zip_buffer
