from fastapi import FastAPI
from fastapi import UploadFile
from fastapi.responses import FileResponse
import re
from google.cloud import documentai_v1 as documentai
import pandas as pd
from datetime import datetime
from fastapi.responses import HTMLResponse

PROJECT_ID = "project-8ac1d017-6b96-435e-978"
LOCATION = "eu"  # ou "us"
PROCESSOR_ID = "20041c8991c17684"

def get_client():
    return documentai.DocumentProcessorServiceClient(
        client_options={"api_endpoint": "eu-documentai.googleapis.com"}
    )

# ==============================
# APPEL DOCUMENT AI
# ==============================

def process_document(content):


    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"

    client = get_client()

    raw_document = documentai.RawDocument(
        content=content,
        mime_type="application/pdf"
    )

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )

    result = client.process_document(request=request)

    return result.document

# ==============================
# EXTRACTION DES DONNÉES
# ==============================

def get_page(entity):
    if entity.page_anchor and entity.page_anchor.page_refs:
        return entity.page_anchor.page_refs[0].page
    # 2. fallback via properties (line_items)
    for prop in entity.properties:
        if prop.page_anchor and prop.page_anchor.page_refs:
            return prop.page_anchor.page_refs[0].page
    return None


def extract_po_list(document):

    po_set = set()

    for entity in document.entities:
        if entity.type_ == "POnumber":
            po_set.add(controlPO(entity.mention_text.strip()))

    return sorted(po_set)

def controlPO(PO):
    if not PO:
        return None
    return PO.split("//")[0]

def extract_delivery(content):
    """
    Extraction des informations de livraison depuis un PDF scanné.
    Retourne :
        po_number (str) : numéro du bon de commande (POxxx)
        df (pd.DataFrame) : colonnes ['POS', 'Shipped', 'Article_No']
    """
    
    document =  process_document(content)


    po_number = None
    po_numbers = []
    po_by_page = {}
    results = []


 #  Récupérer les PO par page
    for entity in document.entities:
        if entity.type_ == "POnumber":
            page = get_page(entity)
            if page is not None:
                po_by_page[page] = controlPO(entity.mention_text)

    # 🔹 2. Récupérer les lignes
    for entity in document.entities:
        if entity.type_ == "line_item":

            page = get_page(entity)
            po = po_by_page.get(page)

            row = {
                "POnumber": po,
                "page": page
            }

            for prop in entity.properties:
                row[prop.type_] = prop.mention_text or ""

            results.append(row)


    po_numbers = extract_po_list(document)   
    po_concat = "_".join(po_numbers)

    df = pd.DataFrame(results)
    if df.empty:
            df = pd.DataFrame([{"message": "no data"}])
    return po_concat, df

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <body>
            <h2>Upload PDF scanné</h2>
            <form action="/process" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="application/pdf" required>
                <br><br>
                <button type="submit">Uploader et traiter</button>
            </form>
        </body>
    </html>
    """


@app.post("/process")
async def process(file: UploadFile):

    content = await file.read()


    provider="Landefeld"

    final_po,df = extract_delivery(content)
    # sécurité si PO vide
    if not final_po:
        final_po = "UNKNOWN"
    final_po = re.sub(r"[^A-Za-z0-9_-]", "", final_po)

    today = datetime.now().strftime("%Y%m%d")
    filename = f"{provider}_{final_po}_{today}.csv"
     
    path = "/tmp/"+filename
    df.to_csv(path, index=False, encoding="utf-8-sig")

    print(f"Processed file: {file.filename}")
    print(f"PO detected: {final_po}")
    print(f"Rows: {len(df)}")

    return FileResponse(
        path=path,
        filename=filename,
        media_type="text/csv"
    )