pip freeze > requirements.txt


sudo apt update
sudo apt install python3-venv
sudo chown -R user:user /var/www/sapb1reportsv2
cd /var/www/sapb1reportsv2
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
pip install django-import-export


pip freeze > /var/www/sapb1reportsv2/backend/requirements.txt


******************
backend api olusturma is plani oncelik sirasi

1- sql sorguyu olustur panele ekle sorguya api ismi ile ayni ismi ver
2- yeni bir api olustur 
(venv) user@reportserver:/var/www/sapb1reportsv2/backend$ python manage.py startapp apiname

3- apiname klasor altinda api, docs. models klasorler olustur
ornek dosya path yapisi
backend/deliverydocsum
backend/deliverydocsum/api
backend/deliverydocsum/api/urls.py
backend/deliverydocsum/api/views.py
backend/deliverydocsum/docs
backend/deliverydocsum/docs/deliverydocsum_api.md
backend/deliverydocsum/docs/sql.md
backend/deliverydocsum/migrations
backend/deliverydocsum/models
backend/deliverydocsum/models/base.py
backend/deliverydocsum/models/models.py
backend/deliverydocsum/__init__.py
backend/deliverydocsum/admin.py
backend/deliverydocsum/apps.py
backend/deliverydocsum/serializers.py
backend/deliverydocsum/tests.py