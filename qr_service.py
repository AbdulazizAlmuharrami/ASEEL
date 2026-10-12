import os
import qrcode
from qrcode.constants import ERROR_CORRECT_H


def verification_url(base_url, unique_code):
    return f"{base_url.rstrip('/')}/verify/{unique_code}"


def qr_filename(unique_code):
    return f"{unique_code}.png"


def generate_qr_image(url, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#1c1916", back_color="#f7f3ea")
    image.save(output_path)
    return output_path
