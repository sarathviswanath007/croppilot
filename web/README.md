# CropPilot web app

A static website: `index.html`, `css/`, `js/` and `data/engine_data.json`. The crop engine runs in the visitor's browser, so there is no server code, database or API key.

## Run locally

From the project folder:

```
python3 scripts/p5_serve.py
```

Then open http://localhost:8000. Stop it with Ctrl+C. The command first copies the latest `data/engine_data.json` into `web/data/` and runs the banned-word check.

(Opening `index.html` directly as a file does not work, because browsers block loading the data file that way.)

## After the data or models change

```
python3 scripts/p3_build_engine_data.py   # rebuild data/engine_data.json
python3 scripts/p5_build_web.py           # copy it into web/ and re-check wording
```

## Deploy to the cloud

Run `python3 scripts/p5_build_web.py`, then upload the whole `web/` folder to any static host, such as Netlify, Cloudflare Pages, GitHub Pages, Firebase Hosting, AWS S3 + CloudFront, Azure Static Web Apps or Google Cloud Storage. No build command is needed. The publish directory is `web`.
