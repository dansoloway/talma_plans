# TALMA plans viewer

- **Source workbook** (`data.xlsx`) stays unchanged; task rows are read with pandas only.
- **Focus areas** in the `Focus Area` column may list one or two comma-separated values. The app normalizes them in Python into `focus_area_1`, `focus_area_2`, and `focus_area_combo`; **order in the spreadsheet does not matter** (e.g. `PD, Full Year` matches `Full Year, PD`).
- **Three or more** distinct values log a warning; the first two after alphabetical sort are kept (see `parse_focus_areas` docstring).

### Setup (virtual environment)

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`

Then:

```bash
pytest
streamlit run app.py
```

### Share online (coworkers)

The lowest-friction option is **[Streamlit Community Cloud](https://streamlit.io/cloud)** (free): connect your **GitHub** account, create a new app, point **Main file** at `app.py`, and use **`requirements.txt`**. You get a URL to share.

- Commit **`data.xlsx`** next to `app.py` if the deployed app should load your real workbook (the default path in the sidebar is already `…/data.xlsx` relative to the app).
- Treat **public repos** as public data: if the spreadsheet is sensitive, use a **private** repo and check Community Cloud’s access rules for your plan.
- Full checklist: [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

**Alternatives** (more setup): [Railway](https://railway.app/), [Render](https://render.com/), or a small VPS with `streamlit run app.py` behind a process manager — usually not “super easy” compared to Community Cloud.
