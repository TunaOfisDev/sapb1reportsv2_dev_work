# bu bloğu bir scratch.py dosyasında çalıştır
from heliosforgev2.models import Image, Chunk
from heliosforgev2.services.image_service import normalize_bbox, overlap_ratio

img = Image.objects.get(file_name="DOC002-PAGE001-IMG001.jpeg")
chk = Chunk.objects.get(chunk_id="0002-PAGE001-CHUNK001")

img_box = normalize_bbox({"bbox": {
    "x0": img.left_x, "x1": img.right_x,
    "bottomY": img.bottom_y, "topY": img.top_y}})
chk_box = {"x0": chk.left_x, "x1": chk.right_x,
           "bottomY": chk.bottom_y, "topY": chk.top_y}

print("ratio =", overlap_ratio(img_box, chk_box))
