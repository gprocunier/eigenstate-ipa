# keytab_rotation_candidates

Renders a read-only report of service or host principals that should be
reviewed for keytab rotation. The role records principal metadata, age, owner,
and the separate remediation workflow that would rotate keys. It never accepts or
renders keytab bytes.

The report object uses the schema identifier
`eigenstate.ipa/keytab_rotation_candidates/v1`.
