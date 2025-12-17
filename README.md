# Textile Project - Ready To Run

## What is included
- `streaming/machine_stream.py` - generates synthetic production records and inserts to Supabase table `production_data`.
- `streaming/supplier_stream.py` - generates synthetic supplier records and inserts to Supabase table `supplier_data`.
- `dashboard.py` - Streamlit dashboard to visualize production & supplier risk.
- `config/config.py` - configuration; uses environment variables `SUPABASE_URL` and `SUPABASE_KEY`.
- `requirements.txt` - packages to install.
- `.env.example` - example environment variables file.
- `models/` - empty folder where models can be saved.

## Quick start (Windows PowerShell)

1. Create & activate venv
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure Supabase credentials (for current session)
   ```powershell
   $env:SUPABASE_URL = "https://your-supabase-url"
   $env:SUPABASE_KEY = "your-service-role-or-anon-key"
   ```
   Or edit `.env.example` and use a tool like `python-dotenv` to load it.

4. Run producer streams (open two terminals)
   ```powershell
   python -m streaming.machine_stream
   python -m streaming.supplier_stream
   ```

5. Run dashboard (another terminal)
   ```powershell
   streamlit run dashboard.py
   ```

6. Open http://localhost:8501 in your browser.

## Notes
- Do NOT commit real secrets to version control. Use environment variables.
- If you don't have a Supabase project, create one at https://supabase.com and create tables `production_data`, `supplier_data`, `risk_alerts` (simple JSON-compatible columns are fine).
- If `xgboost` install is difficult on Windows, you can remove it from `requirements.txt` and use `RandomForestClassifier` during development.
