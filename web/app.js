// DVDPA web front: the same leaks in JavaScript. All identifiers synthetic.
const express = require("express");
const app = express();
app.use(express.json());

function track(user) {
  // ISSUE 4 (rule:pii-to-analytics-js): email and phone to the tag manager and an SDK.
  gtag("event", "signup", { user_email: user.email });
  dataLayer.push({ event: "lead", mobile: user.mobile });
  analytics.identify(user.id, { email: user.email, pan_number: user.panNo });
}

app.post("/signup", (req, res) => {
  // ISSUE 2 (rule:dob-without-age-gate-js): date of birth read, no age check.
  const dob = req.body.dateOfBirth;
  // ISSUE 3 (rule:pii-in-logs-js): identifiers in console output.
  console.log("signup", req.body.email, req.body.mobile);
  track({ id: 1, email: req.body.email, mobile: req.body.mobile, panNo: req.body.panNo });
  res.json({ ok: true, dob });
});

// A gated handler: the scanner must stay quiet here.
app.post("/signup-gated", (req, res) => {
  const dob = req.body.dateOfBirth;
  const age = yearsSince(dob);
  if (age < 18) {
    return res.status(403).json({ error: "parental consent required" });
  }
  res.json({ ok: true });
});

function yearsSince(iso) {
  return Math.floor((Date.now() - new Date(iso).getTime()) / (365.25 * 24 * 3600 * 1000));
}

app.listen(3000);
