makemigrations:
	alembic revision --autogenerate -m "initial commit"

migrate:
	alembic upgrade heads

down-migrate:
	alembic downgrade

current-mig:
	alembic current

celery:
	celery -A core.celery worker --loglevel=info