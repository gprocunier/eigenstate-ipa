# certificate_inventory_report

Renders a safe certificate inventory report from explicit certificate metadata.
The role is read-only and never expects private keys, passwords, tokens, or
certificate payloads. It is intended for scheduled review, renewal planning,
and CI schema checks.

The report object uses the schema identifier
`eigenstate.ipa/certificate_inventory_report/v1`.
