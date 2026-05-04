-- MotherDuck bootstrap for Iceberg-on-R2 mart layer.
-- Idempotent. Run once via scripts/bootstrap_motherduck_iceberg.py.

INSTALL iceberg;
LOAD iceberg;

CREATE OR REPLACE PERSISTENT SECRET r2_pipelines_s3 IN MOTHERDUCK (
    TYPE S3,
    KEY_ID '{KEY}',
    SECRET '{SECRET}',
    ENDPOINT '{ACCOUNT_ID}.r2.cloudflarestorage.com',
    REGION 'auto',
    URL_STYLE 'path',
    SCOPE 's3://{BUCKET}'
);
