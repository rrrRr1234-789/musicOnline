# Delivery Notes

## Project Structure

```text
musicOnline/
  app.py
  README.md
  DELIVERY.md
  requirements.txt
  .env.example
  schema.sql
  database/
    musicOnline.sqlite3
  static/
    css/styles.css
    js/app.js
  templates/
    *.html
  reference-wireframes/
    image1.png ... image10.png
```

## Local Deployment

1. Prepare the environment: Python 3.12 or compatible Python 3, Flask and SQLite.
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Start the website:

```bash
python3 app.py
```

4. Open the website:

```text
http://127.0.0.1:5000
```

## Database Evidence

The Flask app creates `database/musicOnline.sqlite3` automatically. The MySQL table structure required for the assessment is also provided in `schema.sql`.

## Test Accounts

```text
User email: user1@musiconline.com
User password: User12345

Admin username: admin1
Admin password: Admin12345
```
