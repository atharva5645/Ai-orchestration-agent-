import requests
import base64
import os

# Minimal valid PDF file
MINIMAL_PDF_B64 = "JVBERi0xLjAKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQo+PgplbmRvYmoKeHJlZgowIDQKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDEwIDAwMDAwIG4gCjAwMDAwMDAwNjAgMDAwMDAgbiAKMDAwMDAwMDExNyAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDQKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjE3OQolJUVPRgo="

def run_test():
    print("Testing FastAPI Endpoints...")
    
    # 1. Test Health Endpoint
    try:
        health_res = requests.get("http://127.0.0.1:8000/health")
        print(f"Health Check: {health_res.status_code} - {health_res.json()}")
    except Exception as e:
        print(f"Failed to connect to FastAPI server: {e}")
        return

    # 2. Test Document Upload Endpoint
    pdf_path = "dummy_test.pdf"
    with open(pdf_path, "wb") as f:
        f.write(base64.b64decode(MINIMAL_PDF_B64))
        
    print("\nUploading PDF to /api/v1/documents/upload...")
    
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": ("dummy_test.pdf", f, "application/pdf")}
            data = {"ticker": "TEST"}
            upload_res = requests.post("http://127.0.0.1:8000/api/v1/documents/upload", files=files, data=data)
            
        print(f"Upload Status Code: {upload_res.status_code}")
        print(f"Upload Response: {upload_res.json()}")
        
    except Exception as e:
        print(f"Upload failed: {e}")
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    run_test()
