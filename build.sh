
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser non-interactively
if [[ $CREATE_SUPERUSER ]]; then
  python manage.py createsuperuser --no-input
fi

# Seed data (ensure your custom command is idempotent)
python manage.py seed_demo_data