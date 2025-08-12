# GSR Time App (Punch Augmentation)

Flask + PostgreSQL app designed for Render.

## Quick Start (Local)

1. Create and activate a virtualenv.
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and adjust values.
4. Initialize DB:
    ```bash
    flask --app wsgi db init
    flask --app wsgi db migrate -m "init"
    flask --app wsgi db upgrade
    ```
5. Run:
    ```bash
    flask --app wsgi run
    ```

## Deploy to Render

- Push to GitHub.
- Create a new Web Service from this repo.
- Render will provision a PostgreSQL database per `render.yaml`.
- Set `ALLOWED_EMAIL_DOMAIN=gsrconstruct.com` in env vars.

## Notes

- CSVs exported from Patriot Payroll can be uploaded under **Timesheets → Import Patriot CSV**.
- Draft entries autosave. Submitting locks entries.
- Admins can unsubmit latest submitted timesheet per user.
- All mutations recorded in ChangeLog.
