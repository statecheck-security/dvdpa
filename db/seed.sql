-- ISSUE 1 again (in_gstin, in_ifsc, in_upi, in_voter_epic, in_passport,
-- in_driving_licence): a seed file with identifier values. All synthetic.
INSERT INTO customers (full_name, aadhaar_no, pan_no, mobile, email, upi_id, dob) VALUES
  ('Rohan Test', '999999990061', 'CLMPK4420H', '+91-9812345671', 'rohan2@dvdpa-demo.in', 'rohan.test@okaxis', '2010-01-30');

INSERT INTO kyc_documents (customer_id, passport_no, voter_id, dl_no, selfie_path) VALUES
  (1, 'K8765432', 'ABC1234567', 'MH12 20110012345', '/uploads/selfie-1.jpg');

-- Merchant settlement details (a sole proprietor's GSTIN embeds their PAN).
-- gstin: 29BNZPM2501F1ZQ   ifsc: HDFC0001234   account_no: 50100012345678
