import io
import qrcode
from django.core.files.base import ContentFile
from django.utils import timezone


def generer_qr_code(device):
    """Génère un QR code pour un device à partir de son code d'appairage."""
    if not device.code_appairage:
        return None
    
    url = f"geobetail://pair/{device.code_appairage}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#1B3B2F", back_color="#FFFFFF")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()


def sauvegarder_qr_code(device):
    """Génère et sauvegarde le QR code d'un device."""
    qr_data = generer_qr_code(device)
    if qr_data:
        filename = f"qr_{device.code_appairage}.png"
        device.qr_code.save(filename, ContentFile(qr_data), save=False)
        return True
    return False
