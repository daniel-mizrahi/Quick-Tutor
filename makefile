release:
	python manage.py migrate
	python manage.py loaddata app_data.json
	python manage.py loaddata course_data.json
	python manage.py loaddata times.json