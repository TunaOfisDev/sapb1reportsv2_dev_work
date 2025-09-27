**Türkçe karakterlerin HANA DB'den alınan sonuçlarda doğru şekilde görünmesini sağlamak için, 
JSON verilerini işlerken Unicode karakterlerin düzgün şekilde çözülmesini sağlayan bir işlev 
ekleyebilirsiniz. Bu, Python'un json modülünün sağladığı `ensure_ascii=False` parametresi ile yapılabilir. 
Bu parametre, JSON verilerinin ASCII dışı karakterler için Unicode kullanmasını sağlar ve böylece 
Türkçe karakterler gibi non-ASCII karakterlerin doğru şekilde görüntülenmesine 
imkan tanır.

result_data_json = json.dumps(formatted_result_data, ensure_ascii=False)



**result_data alanını kaydederken, doğru JSON formatını kullanmak için 
django.core.serializers.json.DjangoJSONEncoder kullanabilirsiniz.