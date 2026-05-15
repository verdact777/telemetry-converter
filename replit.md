# Python App

A basic interactive Python web app built with Streamlit, featuring a counter, text input, and number slider.

## Run & Operate

- `streamlit run python-app/app.py --server.port 5000` — run the Streamlit app
- The "Start application" workflow runs this automatically

## Stack

- Python 3.11
- Streamlit (interactive web UI)

## Where things live

- `python-app/app.py` — main Streamlit application
- `python-app/.streamlit/config.toml` — Streamlit server configuration

## Architecture decisions

- CORS and XSRF protection disabled so the app works behind the Replit proxy
- App served on port 5000, headless mode enabled for Replit compatibility

## Product

A basic Streamlit app with:
- Interactive counter (increment, decrement, reset)
- Text input with a greeting
- Number slider with progress bar

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- `enableCORS = false` and `enableXsrfProtection = false` are required in `.streamlit/config.toml` for the Replit proxy to work
- Do not use `st.experimental_rerun()` — use `st.rerun()` instead

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
