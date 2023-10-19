run:
	python manage.py runserver 0.0.0.0:8000
	
configure: clean
	python manage.py makemigrations material_carga
	python manage.py migrate
	python manage.py createsuperuser --email admin@logistica.local --username admin

der:
	python manage.py graph_models material_carga --exclude-models=AbstractUser,Group,Permission --exclude-columns=date_joined,is_active,is_staff,is_superuser,first_name,last_name,last_login, -o der_model.png

clean: 
	rm -rf ./material_carga/migrations
	rm -f db.sqlite3

database:
	docker run --name logmatDB -e POSTGRES_PASSWORD=123456 -p 5432:5432 -d postgres