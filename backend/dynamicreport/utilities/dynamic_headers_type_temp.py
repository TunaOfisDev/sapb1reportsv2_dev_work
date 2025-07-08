# backend\dynamicreport\dynamic_headers_type_temp.py
from ..models.models import DynamicHeaders


def generate_dynamic_headers_template(table_name):
    dynamic_headers = DynamicHeaders.objects.filter(table_name=table_name).order_by('line_no')
    headers_template = {}
    
    for dynamic_header in dynamic_headers:
        headers_template[dynamic_header.header_name] = dynamic_header.type
    
    return headers_template


