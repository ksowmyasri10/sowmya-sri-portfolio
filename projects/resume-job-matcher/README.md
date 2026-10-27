# RoleMatch — Private Resume and Job Description Matcher

RoleMatch is a small local-first NLP project that compares the skills explicitly recognized in a resume with the skills explicitly recognized in a job description. It reports matched skills, skills not found in the resume, additional recognized resume skills, and a transparent coverage percentage.

**Privacy:** the application binds to `127.0.0.1`, parses documents and computes matches on your computer, does not call an AI or third-party API, does not log document contents, and does not save resumes or job descriptions. Clear the page inputs when finished. Do not expose the local server to a network.

## Run locally

Requires Python 3.10 or newer. From this directory:

```sh
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# macOS/Linux
source .venv/bin/activate
```

Install document readers and start the application:

```sh
python -m pip install -r requirements.txt
python server.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Paste text or upload TXT, MD, PDF, and DOCX files up to 5 MB. Scanned PDFs require OCR before their text can be compared. After extracting text, edit the fields to remove information you do not want to include.

The app remains entirely local. The upload is sent only to the local Python process in memory; no resume or job description is written to disk.

## How matching works

The matcher uses a curated, transparent skills dictionary and regular-expression aliases (for example, `sklearn` maps to `scikit-learn` and `GenAI` maps to `Generative AI`). The displayed percentage is the share of recognized job-description skills also found in the resume. It is not a hiring prediction, an employer's ATS score, a semantic assessment, or a measure of experience level. An unfamiliar synonym or skill can be missed; review the full posting and tailor your resume truthfully.

## Test and evaluate

Run the unit tests and the small labeled synthetic evaluation set:

```sh
python -m unittest discover -s tests -v
python evaluate.py
```

The synthetic examples are implementation checks, not a general benchmark. Do not interpret their metrics as evidence of recruiting accuracy.
