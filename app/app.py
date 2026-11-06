"""DVDPA: a deliberately leaky KYC signup service.

Every identifier in this repository is synthetic. Aadhaar-shaped values are in
UIDAI's published test range and pass the Verhoeff checksum but were never
issued; PANs, GSTINs and UPI ids are made up and checksum-valid where the
format has one. Nothing here belongs to a person.

Each marked line is a planted issue that dpdp-scan should report. Run:

    pip install -r app/requirements.txt && python app/app.py
    dpdp-scan .
"""

from __future__ import annotations

import logging
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)
logger = logging.getLogger("dvdpa")
logging.basicConfig(level=logging.INFO)


class _Mixpanel:
    """Stands in for an analytics SDK. It only prints; the point is the call site."""

    def track(self, distinct_id: str, event: str, props: dict) -> None:
        print("mixpanel.track", distinct_id, event, props)  # noqa: T201

    def people_set(self, distinct_id: str, props: dict) -> None:
        print("mixpanel.people.set", distinct_id, props)  # noqa: T201


mixpanel = _Mixpanel()

# ISSUE 1 (in_aadhaar, in_pan, in_mobile, email): real-looking identifiers in
# seed data. These are synthetic, but a scanner cannot know that, and neither
# can an attacker who finds the repository. S.8(5), Rule 6(1)(a).
SEED_CUSTOMERS = [
    {
        "name": "Rohan Test",
        "aadhaar_no": "999999990003",
        "pan_no": "BNZPM2501F",
        "mobile": "+91 98123 45670",
        "email": "rohan.test@dvdpa-demo.in",
        "upi_id": "rohan.test@okaxis",
        "dob": "2009-04-18",
    },
    {
        "name": "Priya Demo",
        "aadhaar_no": "999999990035",
        "pan_no": "AKDPS7391Q",
        "mobile": "9123456780",
        "email": "priya.demo@dvdpa-demo.in",
        "upi_id": "priya.demo@ybl",
        "dob": "1994-11-02",
    },
]


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(open("db/schema.sql", encoding="utf-8").read())  # noqa: SIM115
    for c in SEED_CUSTOMERS:
        conn.execute(
            "INSERT INTO customers (full_name, aadhaar_no, pan_no, mobile, email, upi_id, dob)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (c["name"], c["aadhaar_no"], c["pan_no"], c["mobile"], c["email"], c["upi_id"], c["dob"]),
        )
    return conn


@app.post("/signup")
def signup():
    data = request.get_json(force=True) or {}
    # ISSUE 2 (rule:dob-without-age-gate-python): a date of birth is read and
    # stored with no age check anywhere in this function. S.9, Rule 10.
    dob = request.json["dob"]
    # ISSUE 3 (rule:pii-in-logs-python): identifiers written to the log. S.8(5), Rule 6(1)(a).
    logger.info("signup for %s with pan %s", data.get("email"), data.get("pan_no"))
    # ISSUE 4 (rule:pii-to-analytics-python): the email goes to the analytics
    # vendor, a Data Processor, without a stated purpose. S.5, S.6, S.8(2).
    mixpanel.track(data.get("email", ""), "Signed Up", {"email": data.get("email"), "dob": dob})
    return jsonify({"ok": True})


@app.get("/customers/<int:customer_id>")
def customer(customer_id: int):
    row = db().execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    # ISSUE 3 again: logging the whole row.
    logger.debug("served customer %s", row)
    return jsonify(dict(zip([c[0] for c in db().execute("SELECT * FROM customers").description], row, strict=False)))


if __name__ == "__main__":
    app.run(port=5000, debug=False)
