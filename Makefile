mig:
	alembic revision --autogenerate -m "initial commit"
	alembic upgrade heads

down-migrate:
	alembic downgrade

current-mig:
	alembic revision --autogenerate -m "add Star model"
	alembic upgrade head


celery:
	celery -A core.celery worker --loglevel=info