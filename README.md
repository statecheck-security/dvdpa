# DVDPA: a deliberately leaky app for India's DPDP Act

A small KYC signup service that does everything wrong with personal data on purpose,
so you can watch [dpdp-scan](https://github.com/statecheck-security/dpdp-scan) catch it.
Flask on the back, Express on the front, a SQL schema, a Prisma schema and an OpenAPI
contract: the places personal data actually lives in a codebase.

**Every identifier here is synthetic.** Aadhaar-shaped values sit in UIDAI's published
test range and pass the Verhoeff checksum but were never issued. PANs, GSTINs, UPI ids,
IFSC codes and phone numbers are made up and checksum-valid where the format has one.
Email addresses use a domain that is not registered. Nothing belongs to a person.

> **Not legal advice.** The sections of the Digital Personal Data Protection Act, 2023
> and the DPDP Rules, 2025 quoted below are pointers for engineers. Whether a finding
> matters in a real system depends on your processing, your contracts and how the Data
> Protection Board reads the Rules.

## Run the scan

```bash
pipx install dpdp-scan semgrep      # or: pip install dpdp-scan semgrep
# until the PyPI release lands: pip install git+https://github.com/statecheck-security/dpdp-scan@v0.1.0 semgrep
git clone https://github.com/statecheck-security/dvdpa && cd dvdpa
dpdp-scan .
```

Without Semgrep the value detectors and schema classifier still run; the six rule
findings below need it. The repository's own workflow runs the
[dpdp-scan Action](https://github.com/statecheck-security/dpdp-scan/blob/main/action.yml)
on every push and sends the SARIF to this repository's Security tab.

To run the app itself (it is not needed for the scan):

```bash
pip install -r app/requirements.txt && python app/app.py
```

## What is planted, and what dpdp-scan reports

13 files, 66 findings, all intended.

| Issue | Where | Detector | What the finding engages |
|---|---|---|---|
| 1. Real-looking identifiers in seed data and fixtures | `app/app.py`, `db/seed.sql`, `fixtures/customers.json` | `in_aadhaar` 4, `in_pan` 4, `in_mobile` 4, `email` 4, `in_upi` 4, `in_gstin` 2, `in_ifsc` 2, `in_passport` 1, `in_voter_epic` 1, `in_driving_licence` 1 | S.8(5) safeguards; Rule 6(1)(a) masking and encryption |
| 2. Date of birth read from the request with no age gate in the function | `app/app.py` `/signup`, `web/app.js` `/signup` | `rule:dob-without-age-gate-python` 1, `rule:dob-without-age-gate-js` 1 | S.9 children; Rule 10 verifiable parental consent |
| 3. Identifiers written to logs | `app/app.py`, `web/app.js` | `rule:pii-in-logs-python` 1, `rule:pii-in-logs-js` 1 | S.8(5); Rule 6(1)(a) |
| 4. Identifiers sent to analytics SDKs and the tag manager | `app/app.py` (Mixpanel), `web/app.js` (gtag, dataLayer, Segment-style identify) | `rule:pii-to-analytics-python` 1, `rule:pii-to-analytics-js` 3 | S.5 notice, S.6 consent, S.8(2) processors |
| 5. Personal-data fields declared with no protection or retention rule | `db/schema.sql`, `prisma/schema.prisma`, `api/openapi.yaml` | `schema_sql` 11, `schema_prisma` 11, `schema_openapi` 9 | S.4 purpose, S.5 notice, S.8(7) erasure, S.8(5), Rule 6(1)(a); `dob` also S.9 |

Two things that must **not** be reported, and are not:

- `plans.name` in `db/schema.sql` and `Plan.name` in Prisma: a `name` column only counts
  in a table about people.
- `/signup-gated` in `web/app.js`: the same `req.body.dateOfBirth` read, but with
  `if (age < 18)` in the handler, so the age-gate rule stays quiet.

Every reported value is masked in the output (`********0003`); dpdp-scan never prints
what it finds.

## Fixing it

Each issue has a conventional fix, and each fix changes the scan:

| Issue | Fix | Scan after the fix |
|---|---|---|
| 1 | Replace seed values with placeholders; keep real test data out of the repo | the value findings disappear |
| 2 | Compute age from the date of birth and gate under-18 signups behind parental consent | the `dob-without-age-gate` findings disappear |
| 3 | Log an opaque customer id; redact fields in the logger | `pii-in-logs` disappears |
| 4 | Send a hashed id to analytics; state the purpose in the notice; sign a processor contract | `pii-to-analytics` disappears |
| 5 | Record each field in the data map with a purpose and retention period; encrypt identifiers at the field level | the schema findings stay (the fields still exist) but now have an owner |

The `.dpdp-scan.yml` here keeps everything switched on. A real project adds its own mailbox
domains under `allow.domains`, points `ignore.paths` at fixtures, and sets `fail_on`.

## Licence

Apache License 2.0. Built by [StateCheck Security](https://statechecksecurity.com) as the
demo target for dpdp-scan. Contributions of further planted issues are welcome, as long as
every value stays synthetic.
