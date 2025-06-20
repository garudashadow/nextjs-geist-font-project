import csv
import json
import os
from datetime import datetime

def csv_to_json(csv_filepath, json_filepath):
    companies = []
    with open(csv_filepath, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            company = {
                'company_name': row.get('nama_perusahaan', '').strip(),
                'address': row.get('alamat_lengkap', '').strip(),
                'emails': [email.strip() for email in row.get('email_kontak', '').split(',') if email.strip()],
                'phones': [phone.strip() for phone in row.get('nomor_telepon', '').split(',') if phone.strip()],
                'hrd_name': row.get('nama_hrd', '').strip(),
                'source': 'CSV Import',
                'scraped_at': datetime.now().isoformat()
            }
            companies.append(company)
    
    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_companies": len(companies),
            "location": "Kabupaten Bekasi, Jawa Barat",
            "data_sources": ["CSV Import"]
        },
        "companies": companies
    }
    
    with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(output_data, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"✅ Berhasil mengonversi {len(companies)} perusahaan dari CSV ke JSON: {json_filepath}")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), 'perusahaan_bekasi.csv')
    json_path = os.path.join(os.path.dirname(__file__), f'bekasi_companies_csv_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    csv_to_json(csv_path, json_path)
