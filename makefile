run:
	pyhthon manage.py runserver
	
configure: clean
	python manage.py makemigrations material_carga
	python manage.py migrate
	python manage.py createsuperuser --email admin@logistica.local --username admin

clean: 
	rm -rf ./material_carga/migrations
	rm -f db.sqlite3