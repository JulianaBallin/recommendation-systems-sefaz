import json
import urllib.request
import urllib.parse
import csv
import os
import shutil
import mimetypes

API_URL = "http://127.0.0.1:8000"
DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../dataset"))
PROCESSADO_DIR = os.path.join(DATASET_DIR, "processado")
STANDARDIZED_DIR = os.path.join(DATASET_DIR, "standardized")

def setup():
    if os.path.exists(PROCESSADO_DIR):
        shutil.rmtree(PROCESSADO_DIR)
    if os.path.exists(STANDARDIZED_DIR):
        shutil.rmtree(STANDARDIZED_DIR)
    os.makedirs(PROCESSADO_DIR, exist_ok=True)

def post_multipart(url, fields, files):
    boundary = '----------BoundaryString'
    lines = []
    for name, value in fields.items():
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="{}"'.format(name))
        lines.append('')
        lines.append(value)
    
    for name, (filename, content, content_type) in files.items():
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="{}"; filename="{}"'.format(name, filename))
        lines.append('Content-Type: {}'.format(content_type))
        lines.append('')
        lines.append(content)
    
    lines.append('--' + boundary + '--')
    lines.append('')
    body = '\r\n'.join(lines).encode('utf-8')
    
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type', 'multipart/form-data; boundary={}'.format(boundary))
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

def read_csv_rows(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def test_upload_usuarios():
    print("Testing Upload Users...")
    csv_content = "cpf,nome,data_nasc\n52998224725,Teste User,1990-01-01\n11111111111,Invalid Cpf,1990-01-01"
    
    files = {"file": ("users.csv", csv_content, "text/csv")}
    status, response_text = post_multipart(f"{API_URL}/usuarios/upload", {}, files)
    
    if status == 200:
        print("Upload Users: OK")
        print(response_text)
        
        if os.path.exists(os.path.join(PROCESSADO_DIR, "clientes.csv")):
            try:
                rows = read_csv_rows(os.path.join(PROCESSADO_DIR, "clientes.csv"))
                print(f"Clientes CSV rows: {len(rows)}")
                if len(rows) >= 1:
                    print("Persistence Users: OK")
                else:
                    print("Persistence Users: FAILED (Empty)")
            except Exception as e:
                 print(f"Persistence Users: FAILED (Read Error: {e})")
        else:
            print("Persistence Users: FAILED (File not found)")
    else:
        print(f"Upload Users: FAILED ({status})")
        print(response_text)

def test_upload_nfs():
    print("\nTesting Upload NFs...")
    csv_content = "descricao,supermercado\nLEITE CONDENSADO MOCOCA 395G,SUPERMERCADO A\nSABONETE DOVE ORIGINAL 90G,SUPERMERCADO B\nPRODUTO DESCONHECIDO XYZ,SUPERMERCADO C"
    
    files = {"file": ("nfs.csv", csv_content, "text/csv")}
    status, response_text = post_multipart(f"{API_URL}/nfs/upload", {}, files)
    
    if status == 200:
        print("Upload NFs: OK")
        print(response_text)
        
        processado_path = os.path.join(PROCESSADO_DIR, "nfs_processadas.csv")
        if os.path.exists(processado_path):
            try:
                rows = read_csv_rows(processado_path)
                print(f"NFs Processadas rows: {len(rows)}")
                if rows and "marca" in rows[0]:
                    print("Brand Extraction: OK")
                    print(f"Sample: {rows[0]['descricao']} | {rows[0]['marca']}")
                else:
                    print("Brand Extraction: FAILED (Column missing or empty)")
            except Exception as e:
                print(f"Persistence NFs: FAILED (Read Error: {e})")
        else:
            print("Persistence NFs: FAILED (File not found)")
            
        std_path = os.path.join(STANDARDIZED_DIR, "produtos_padronizados.csv")
        if os.path.exists(std_path):
            try:
                rows = read_csv_rows(std_path)
                print(f"Standardized rows: {len(rows)}")
                if len(rows) >= 1:
                     print("TF-IDF Standardization: OK")
                else:
                     print("TF-IDF Standardization: FAILED (Empty)")
            except Exception as e:
                print(f"TF-IDF Standardization: FAILED (Read Error: {e})")
        else:
            print("TF-IDF Standardization: FAILED (File not found)")
            
    else:
        print(f"Upload NFs: FAILED ({status})")
        print(response_text)

if __name__ == "__main__":
    setup()
    try:
        test_upload_usuarios()
        test_upload_nfs()
    except Exception as e:
        print(f"An error occurred: {e}")
