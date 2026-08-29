# Untuk penyedia yang membaca Procfile alih-alih Dockerfile (Railway tanpa
# Docker, Heroku). Dijalankan dari akar repo.
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
