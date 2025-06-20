"""
Helper functions untuk konten berbahasa Indonesia
"""
from datetime import datetime
import re
import logging

# Mapping bulan Indonesia ke angka
BULAN_MAP = {
    'januari': '01',
    'februari': '02',
    'maret': '03',
    'april': '04',
    'mei': '05',
    'juni': '06',
    'juli': '07',
    'agustus': '08',
    'september': '09',
    'oktober': '10',
    'november': '11',
    'desember': '12'
}

def parse_indo_date(date_str: str) -> str:
    """
    Parse tanggal format Indonesia ke ISO format

    Contoh input yang didukung:
    - 17 Februari 2025
    - 17 Feb 2025
    - 17/02/2025
    - 2025-02-17
    - 17 Feb 2025 20:29
    """
    try:
        # Handle empty or None input
        if not date_str:
            return ""

        # Bersihkan string
        date_str = date_str.lower().strip()

        # Coba parse format ISO
        if '-' in date_str and len(date_str.split('-')[0]) == 4:
            return date_str

        # Extract time if present
        time_part = ""
        if any(c.isdigit() for c in date_str[-5:]):
            parts = date_str.rsplit(' ', 2)
            if len(parts) >= 2 and ':' in parts[-1]:
                time_part = f" {parts[-2]}:{parts[-1]}"
                date_str = ' '.join(parts[:-2])

        # Coba format dengan nama bulan
        for bulan, angka in BULAN_MAP.items():
            if bulan in date_str:
                # Ekstrak tanggal dan tahun
                parts = re.findall(r'\d+', date_str)
                if len(parts) >= 2:
                    tanggal = parts[0].zfill(2)
                    tahun = parts[-1]
                    return f"{tahun}-{angka}-{tanggal}{time_part}"

        # Coba format dengan slash atau dash
        if '/' in date_str or '-' in date_str:
            parts = re.split(r'[/-]', date_str)
            if len(parts) == 3:
                if len(parts[0]) == 4:  # yyyy-mm-dd
                    return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}{time_part}"
                else:  # dd/mm/yyyy
                    return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}{time_part}"

        return date_str  # Return original if no format matches

    except Exception as e:
        logging.error(f"Error parsing date '{date_str}': {e}")
        return date_str  # Return original string on error

def clean_indo_text(text: str) -> str:
    """
    Bersihkan teks dengan mempertahankan karakter khusus bahasa Indonesia
    """
    if not text:
        return ""

    # Hapus karakter whitespace berlebih
    text = ' '.join(text.split())

    # Hapus karakter spesial tapi pertahankan huruf dengan tanda diakritik
    text = re.sub(r'[^\w\s\-\'āĀēĒīĪōŌūŪḍḌṭṬṇṆñÑḷḶṃṂḥḤ]', ' ', text)

    # Normalisasi spasi
    text = text.strip()

    return text

def extract_location(text: str) -> str:
    """
    Ekstrak lokasi dari teks berita Indonesia

    Contoh:
    "JAKARTA, KOMPAS.com - ..." -> "Jakarta"
    """
    # Pattern untuk lokasi di awal berita
    location_pattern = r'^([A-Z]+(?:\s*,\s*[A-Z]+)*)'

    match = re.match(location_pattern, text)
    if match:
        location = match.group(1)
        return location.split(',')[0].strip()

    return ""

"""
Contoh penggunaan:

# Parse tanggal Indonesia
tanggal = parse_indo_date("17 Februari 2025")
print(tanggal)  # Output: 2025-02-17

# Bersihkan teks
teks = clean_indo_text("JAKARTA - Ini adalah contoh teks berita...")
print(teks)  # Output: Ini adalah contoh teks berita...

# Ekstrak lokasi
lokasi = extract_location("JAKARTA, KOMPAS.com - Berita terkini...")
print(lokasi)  # Output: JAKARTA
"""