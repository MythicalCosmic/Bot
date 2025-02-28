1. `virtualenv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `rm database.db`
6. `alembic upgrade head`
7. `python3 main.py`