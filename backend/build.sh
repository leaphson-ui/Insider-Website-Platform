#!/bin/bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run any database migrations if needed
# python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

echo "Build completed successfully"
