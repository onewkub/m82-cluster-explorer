# Deploy to Cloudflare

This project is hosted on Cloudflare Pages using Direct Upload. The project name is `m82-cluster-explorer`, and its production branch is `main`.

## Update the live website

After checking the changes and committing the intended website version:

```sh
npx wrangler login
npx wrangler pages deploy dist --project-name m82-cluster-explorer --branch main
```

The website is available at https://m82-cluster-explorer.pages.dev/ . A GitHub push or release does not trigger a new deployment automatically in this setup.

## Custom domain

Intended domain: `m82-cluster-explorer.onew.dev`.

The domain is registered in the project's Custom domains settings. DNS must contain a CNAME named `m82-cluster-explorer` pointing to `m82-cluster-explorer.pages.dev`. Wait for the Pages custom domain status and HTTPS certificate to become active before distributing the custom URL as the live demo.

## Local state

Wrangler credentials are kept outside this repo. `.wrangler/` is ignored. Never commit Cloudflare credentials or tokens.

The Python scripts are not needed on Cloudflare: only files inside `dist/` are uploaded. The deployment ZIP in GitHub Releases contains those same website files at its root.
