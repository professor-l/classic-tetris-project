# Web Setup

This guide assumes you've already gone through the steps of either [SETUP_QUICK.md](SETUP_QUICK.md) or [SETUP_ROBUST.md](SETUP_ROBUST.md). We will now go through the process of running the bot's website.

### (recommended) Database setup

In the previous setup guide, we set our database as SQLite for convenience. However, the production build of the bot uses PostgreSQL, so we'll show you how to set that up here. I'm pretty sure things will still work without this step, but you should complete this if you want to load in an example database (actually, a snapshot of the production db).

Start by installing and running PostgreSQL. Use your preferred method, be it the [download page]([https://www.postgresql.org/download/](https://www.postgresql.org/download/)) or your package manager.

Next, you'll need to run
```bash
pip install -r requirements_prod.txt
```
which will allow the Python code to interface with PostgreSQL. Afterwards, add this line to your `.env` file:
```bash
DATABASE_URL="postgres:///tetris"
```

Finally, you'll want to install the example database. This step requires a *database dump file*, which you can get from **fractal** or **dexfore** (message `fractal161` or `dexfore` on Discord). Once you have that, run
```bash
script/restore_dump.sh path/to/file.dump
```
to set everything up.

### Running tests

The project has a modest testing suite, which you can invoke simply with
```bash
pytest
```
Make sure most of the tests pass (preferably they all do, but things will \*probably* work well enough even if they don't). You should see tests being run in both `classic_tetris_project/tests/` and `classic_tetris_project/private/tests/`.

### Superuser account

To access the admin panel, you'll naturally need an admin account, which you can create through this command:
```bash
python manage.py createsuperuser
```

### gotham.ttf

NOTE: this step is highly undesirable and will hopefully become unnecessary in the future.

Background: one of the site's features is providing an alternate font face for use in brackets. The [Gotham typeface](https://typography.com/fonts/gotham/overview) was chosen, but unfortunately [our license](/LICENSE) doesn't let us include it in the repo. Furthermore, things break without the file, so all you need to do is find a `ttf` file somewhere (it doesn't even have to be Gotham), and then save it to `./classic_tetris_project/private/assets/fonts/gotham.ttf`.

### Running the webserver

Home stretch! Start by installing the required node packages using
```bash
npm install
```
You can then run the [webpack](https://webpack.js.org/) server with
```bash
npm start
```
This command will first build the frontend and then continue running, rebuilding when it detects that a file has changed. You need to run this at least once (otherwise there's nothing for the server to serve).

Finally, to run the *actual* webserver you invoke
```bash
python manage.py runserver
```
and once that's running you can view it at http://localhost:8000.

### (optional) Host mapping

If you would like to view the dev server using a different url (e.g. `dev.monthlytetris.info`), you can map it to `127.0.0.1` in your [hosts file](https://en.wikipedia.org/wiki/Hosts_(file)).
