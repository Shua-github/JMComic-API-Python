import img2pdf
from pypdf import PdfWriter, PdfReader
from io import BytesIO
import zipfile
import os
from typing import Literal, List
import pyzipper


def merge_images_to_file(
    image_paths: List[str],
    out_file_format: Literal["pdf", "zip"],
) -> BytesIO:
    """
    合并图片为 PDF 或 ZIP 文件
    """
    if out_file_format == "pdf":
        pdf_bytes = img2pdf.convert(image_paths)
        pdf_stream = BytesIO(pdf_bytes)
        pdf_stream.seek(0)
        return pdf_stream
    elif out_file_format == "zip":
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for img_path in image_paths:
                arcname = os.path.basename(img_path)
                zipf.write(img_path, arcname=arcname)
        zip_buffer.seek(0)
        return zip_buffer
    else:
        raise ValueError(f"Unsupported file format: {out_file_format}")


def encrypt_file(
    input_file: BytesIO,
    password: str,
    file_type: Literal["pdf", "zip"],
) -> BytesIO:
    """
    加密 PDF 或 ZIP 文件，输入为 BytesIO，输出加密后的 BytesIO。
    """
    if not password:
        return input_file

    if file_type == "pdf":
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()

        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

        pdf_writer.encrypt(password)

        encrypted_pdf = BytesIO()
        pdf_writer.write(encrypted_pdf)
        encrypted_pdf.seek(0)
        return encrypted_pdf

    elif file_type == "zip":
        zip_buffer = BytesIO()
        with pyzipper.AESZipFile(
            zip_buffer,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES,
        ) as zipf:
            zipf.setpassword(password.encode("utf-8"))  # 先设置密码

            with zipfile.ZipFile(input_file, "r") as existing_zip:
                for file_name in existing_zip.namelist():
                    file_data = existing_zip.read(file_name)
                    zipf.writestr(file_name, file_data)

        zip_buffer.seek(0)
        return zip_buffer

    else:
        raise ValueError(f"Unsupported file format: {file_type}")


class GetCacheFilePath:
    def __init__(self, output_dir: str, jm_id: int):
        self.output_dir = output_dir
        self.jm_id = str(jm_id)

    def get(self, file_type: Literal["pdf", "zip", "png"]):
        return os.path.join(self.output_dir, self.jm_id, file_type)
