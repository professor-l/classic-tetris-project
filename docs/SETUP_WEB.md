# Web Setup

1. Follow SETUP_QUICK.md
2. Install the `private` submodule
3. Map `dev.monthlytetris.info` to `127.0.0.1` in your `/etc/hosts` file or equivalent
4. Install and run postgresql (through [https://www.postgresql.org/download/](https://www.postgresql.org/download/) or a package manager)
5. Install and run redis (through [https://redis.io/download](https://redis.io/download) or a package manager)
6. Install Python bindings for postgres:
   ```
   pip install -r requirements_prod.txt
   ```
7. Run tests and ensure they pass:
   ```
   pytest
   ```
   You should see tests being run in both `classic_tetris_project/tests/` and `classic_tetris_project/private/tests/`.
8. In your `.env` file, uncomment or add the following line:
   ```
   DATABASE_URL="postgres:///tetris"
   ```
9. Install a database dump from production
   - Get a dump from dexfore
   - Run `script/restore_dump.sh path/to/file.dump`
   - If you don't already have access to a superuser account:
     ```
     python manage.py createsuperuser
     ```
     This will create a superuser account; you can log in with these credentials later at http://dev.monthlytetris.info:8000/admin/ and give your own user superuser privileges.
10. Install Node packages:
   ```
   npm install
   ```
11. Run the server:
   - Webpack dev server (w/ file listener): `npm start`
   - Django server: `python manage.py runserver`

   You should now be able to access the web server at http://dev.monthlytetris.info:8000/
