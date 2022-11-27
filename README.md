![](./ops/ai-library-1.png)

# Gideon

### What is this?

- An attempt at AI-first legal tooling.
- Frontend companion (treat it as a sidebar) runs at port `1111`.
- Backend API file parser + ai functions run at port `3000`
- Postgres DB running at port `5432`

### Run it Locally

1. Create a file in the root of this repo called `.env`, and copy values from the gist, notion page, or whever it's being stored atm. It'll be minimal vars, the rest are fetched at runtime
2. Spin up the frontend/backend from the root of this repo with `docker-compose up` (when api requirements change, rebuild the api with `docker-compose build api`)
3. Once running, go to directory `databases/app` and run migrations with `alembic upgrade head`
4. Then from the same directory, seed the database with a user/case via `python seed.py`
5. You're good to go! Just go to `localhost:1111`, click through the login/case views, and start uploading files + querying!

### Production Deploys/Migrations

Want to deploy some changes for others to use?

- To deploy, we'll specify an environment and service with our deploy.sh script (ex: `bash deploy.sh <TARGET_ENV> <SERVICE>`)
  - `bash deploy.sh production api`
  - `bash deploy.sh production defender`
  - `bash deploy.sh production frontdoor`
- To migrate a database with some new revisions, we'll use our manage.sh script (ex: `bash manage.sh <TARGET_ENV> <COMMAND> <DIRECTION>`)
  - `bash manage.sh local migrate-app head`
  - `bash manage.sh local migrate-app rollback`
  - `bash manage.sh production migrate-app head`

### Gotcha's Currently

- Running Sanic with multiple workers/dev doesn't work in a docker container. Restart the API after changes have been made by typing in a separate shell `docker-compose restart api`. You can keep the cluster running.

---

![](./ops/ai-library-2.png)
