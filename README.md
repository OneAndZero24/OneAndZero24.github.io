# Jan Miksa — research website

Minimalist academic website built with [Hugo](https://gohugo.io) on top of the
[hugo-website template](https://github.com/pmichaillat/hugo-website) (PaperMod
theme). The publication list is synchronized automatically with
[Google Scholar](https://scholar.google.com/citations?user=bTL7lzgAAAAJ) and
the CV PDF is generated from structured data, so the website, the CV, and
LinkedIn all tell the same story.

## Structure

```
config/_default/hugo.yaml   site configuration (menu, homepage, social links)
config/development/hugo.yaml local dev override (serves at http://localhost:1313/)
content/                    homepage copy lives in config; plus:
  publications/_index.md    publications page (rendered from data/)
  projects.md               ActivationScope
data/
  cv.yaml                   CV source of truth (experience, education, skills)
  publications_manual.yaml  manual overrides + manual-only publications
  publications.yaml         GENERATED: merged list used by site + CV
  scholar_cache.yaml        GENERATED: raw Scholar snapshot (committed)
layouts/                    custom homepage, publications page, partials
assets/css/extended/        site CSS (homepage spacing, publication styles)
scripts/
  sync_publications.py      Scholar sync + manual merge
  generate_cv.py            cv/cv.tex + static/cv.pdf from data
cv/cv.tex                   GENERATED: LaTeX source of the CV
static/cv.pdf               GENERATED: compiled CV served by the site
.github/workflows/
  hugo.yml                  build + deploy on every push
  sync.yml                  weekly Scholar sync, CV rebuild, commit + deploy
```

## Common tasks

Install the Python dependencies once:

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

Then:

```bash
make serve          # local preview at http://localhost:1313/ (hugo server)
make site           # build into public/
make sync           # merge cached Scholar data + manual overrides (offline)
make sync-online    # fetch from Google Scholar, then merge
make cv             # regenerate cv/cv.tex and compile static/cv.pdf
```

To edit a publication (fix venue, add code link, change status, reorder), edit
`data/publications_manual.yaml` and run `make sync`. To add a paper that is not
on Scholar yet, add it to the `entries:` list in the same file. Never edit
`data/publications.yaml` by hand — it is regenerated.

To edit the CV, change `data/cv.yaml` (or `data/publications_manual.yaml` for
publication lines) and run `make cv`.

## Automatic updates

The workflow `.github/workflows/sync.yml` runs every Monday:

1. fetches the publication list from Google Scholar,
2. merges it with the manual overrides,
3. regenerates the CV PDF,
4. commits `data/`, `cv/`, and `static/cv.pdf` if anything changed,
5. rebuilds and deploys the site.

Google Scholar blocks anonymous scraping intermittently. If a scheduled fetch
fails, the workflow keeps the last committed data (no breakage), and the next
run tries again. For a more reliable sync, create a [SerpAPI](https://serpapi.com)
account and add the key as the repository secret `SERPAPI_API_KEY`; the script
detects it automatically and uses the API instead of scraping.

## Deployment

The site is deployed by GitHub Actions to GitHub Pages. Set the final URL in
`config/_default/hugo.yaml` (`baseURL`) once the repository and domain are
known. The
canonical URL of the live site should match it.

## License

Template code: MIT (see `LICENSE.md`). Site content © Jan Miksa.
