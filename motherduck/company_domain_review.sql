-- Repo-owned review seed for broad-discovery company/domain relevance.
-- Decisions:
--   approved: company passes the company/domain gate
--   rejected: company is blocked even if deterministic keywords match
--   pending: company remains hidden pending manual review

CREATE OR REPLACE TABLE company_domain_review AS
SELECT *
FROM (
    VALUES
        ('remoteok', 'Natera', 'rejected', 'Generic healthcare/biotech platform company; not a mission/domain fit for the radar.', DATE '2026-05-13'),
        ('remoteok', 'Quanata', 'rejected', 'Insurance-adjacent technology company; not outdoor/geospatial/climate/civic mission fit.', DATE '2026-05-13'),
        ('remoteok', 'Civitech', 'approved', 'Civic tech/public-benefit democracy infrastructure; mission/domain fit if location also qualifies.', DATE '2026-05-13'),
        ('remoteok', 'Valon Mortgage', 'rejected', 'Generic mortgage/fintech company; not a mission/domain fit.', DATE '2026-05-13'),
        ('remoteok', 'Cast AI', 'rejected', 'Generic cloud/infrastructure optimization company; not a mission/domain fit.', DATE '2026-05-13'),
        ('remoteok', 'Contact Government Services, LLC', 'pending', 'Government services may be relevant only if role/company context shows civic/public infrastructure fit.', DATE '2026-05-13'),
        ('remoteok', 'Prove', 'pending', 'Identity/security company needs manual review before broad-discovery display.', DATE '2026-05-13')
) AS t(source_kind, company, decision, reason, updated_at);
