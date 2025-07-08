# backend/systemnotebook/utils/tag_extractor.py

import re

def extract_tags_from_content(content, known_tags=None):
    """
    İçerikten app adları veya özel etiketleri tespit eder.
    Örnek: 'productconfig güncellendi' → ['productconfig']
    """
    if not known_tags:
        known_tags = [
            'productconfig', 'report_orchestrator', 'mailservice', 'totalrisk',
            'hanadbcon', 'logodbcon', 'dynamicreport', 'salesbudgetv2', 'openorderdocsum'
        ]

    found_tags = []
    for tag in known_tags:
        pattern = r'\b' + re.escape(tag) + r'\b'
        if re.search(pattern, content, flags=re.IGNORECASE):
            found_tags.append(tag)

    return found_tags
