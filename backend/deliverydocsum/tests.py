from django.conf import settings
from utilities.data_fetcher import fetch_hana_db_data

token = settings.HANA_ACCESS_TOKEN
data = fetch_hana_db_data(token)
print(data)
