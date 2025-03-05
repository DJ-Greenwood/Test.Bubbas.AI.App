# Bubbas.ai Deployment Guide

This guide outlines the steps to deploy the Bubbas.ai application as per the Stage 1: Proof of Concept requirements.

## Prerequisites

- Python 3.8+ installed
- Git installed
- OpenAI API key
- Domain registered (bubbas.ai)

## Local Development Setup

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd bubbas_ai
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    ```bash
    # On Linux/macOS
    export OPENAI_API_KEY=your_openai_api_key
    export DJANGO_SECRET_KEY=your_django_secret_key
    
    # On Windows
    set OPENAI_API_KEY=your_openai_api_key
    set DJANGO_SECRET_KEY=your_django_secret_key
    ```

5. Run migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

7. Run the development server:
    ```bash
    python manage.py runserver
    ```

8. Access the application at http://localhost:8000

## Production Deployment

### Database Setup

For the POC, we're using SQLite as specified in the requirements. However, for a more robust production environment, consider migrating to PostgreSQL in future versions.

### Django Application Deployment

1. Update the settings for production:
    - Set `DEBUG = False` in settings.py
    - Update `ALLOWED_HOSTS` with your domain
    - Set a strong `SECRET_KEY`

2. Collect static files:
    ```bash
    python manage.py collectstatic
    ```

3. Deploy using Gunicorn:
    ```bash
    gunicorn bubbas_ai.wsgi:application
    ```

### Web Server Configuration

For a simple deployment, you can use Nginx as a reverse proxy:

```nginx
server {
     listen 80;
     server_name bubbas.ai www.bubbas.ai;

     location = /favicon.ico { access_log off; log_not_found off; }
     
     location /static/ {
          root /path/to/bubbas_ai;
     }

     location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
     }
}
```

### Setting up HTTPS

Use Certbot to configure HTTPS:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d bubbas.ai -d www.bubbas.ai
```

### Domain Configuration

1. Point your domain (bubbas.ai) to your server's IP address using A records in your DNS settings
2. Configure the www subdomain as well

## Testing and Beta Release

1. Conduct internal testing to ensure all features work correctly
2. Set up a