# DuckQuake

Seismic monitoring and visualization of crowd noise at Autzen Stadium, from
stations UO.DUCK1-3.

Code lives here. Data, analysis, and documents live in `~/DuckQuake`.

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The python.org build of Python on macOS ships without root certificates, so
HTTPS from Python fails. Either run `Install Certificates.command` from the
Python application folder once, or set the certifi bundle for each session:

```bash
export SSL_CERT_FILE="$(.venv/bin/python -m certifi)"
```

## Archive data

`config.toml` names the archive windows (`[archive.*]`) and the data
directory. Download station metadata and all windows with:

```bash
.venv/bin/python scripts/download_archive.py
```

Pass dataset names to download only some. Existing files are skipped.
