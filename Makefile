.PHONY: help build run stop restart logs clean test

# Default target
help:
	@echo "SmartStock DevOps Commands"
	@echo "--------------------------------------------------------"
	@echo "make run         : Run the Streamlit app locally (no Docker)"
	@echo "make build       : Build the Docker image"
	@echo "make up          : Start the Docker container (detached)"
	@echo "make down        : Stop and remove the Docker container"
	@echo "make logs        : View Docker container logs"
	@echo "make clean       : Remove Python cache files"
	@echo "make generate    : Regenerate ML offline artifacts"

run:
	streamlit run app.py

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

generate:
	python generate_artifacts.py
