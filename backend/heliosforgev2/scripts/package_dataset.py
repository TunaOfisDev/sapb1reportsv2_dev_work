# backend/heliosforgev2/scripts/package_dataset.py

import os, json, tqdm, shutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import argparse

BASE = "/var/www/sapb1reportsv2/backend/heliosforgev2/storage"
IMAGE_DIR = f"{BASE}/images"
OUTPUT_DIR = "/var/www/sapb1reportsv2/dataset_out"

def package_dataset(doc_id: str):
    out_dir = os.path.join(OUTPUT_DIR, doc_id)
    os.makedirs(os.path.join(out_dir, "images"), exist_ok=True)

    json_path = os.path.join(BASE, "json", f"{doc_id}_parsed.json")
    if not os.path.exists(json_path):
        print(f"[✗] JSON dosyası bulunamadı: {json_path}")
        return

    # 1) chunks.parquet
    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    df = pd.json_normalize(chunks)
    pq.write_table(pa.Table.from_pandas(df), os.path.join(out_dir, "chunks.parquet"))

    # 2) Manifest ve görsellerin kopyalanması
    manifest = []
    for file in os.listdir(IMAGE_DIR):
        if not file.startswith(doc_id):
            continue
        src = os.path.join(IMAGE_DIR, file)
        dst = os.path.join(out_dir, "images", file)
        shutil.copy(src, dst)

        # Sayfa numarasını filename'den çıkar
        try:
            page_num = int(file.split("PAGE")[1][:3])
        except:
            page_num = None

        manifest.append({
            "id": file.split(".")[0],
            "file_name": file,
            "page_num": page_num
        })

    with open(os.path.join(out_dir, "manifest.jsonl"), "w", encoding="utf-8") as f:
        for row in manifest:
            f.write(json.dumps(row) + "\n")

    print(f"✅ {doc_id} paketi tamamlandı → {out_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc-ids", nargs="+", required=True, help="Örn: DOC008 DOC009 DOC010")
    args = parser.parse_args()

    for doc_id in tqdm.tqdm(args.doc_ids):
        package_dataset(doc_id)
