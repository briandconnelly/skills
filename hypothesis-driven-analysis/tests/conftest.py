# s3-bug is an intentionally failing fixture: test_parse_dates is the bug an S3
# scenario agent is scored on finding. Excluded from collection; do not fix it.
collect_ignore = ["fixtures/s3-bug"]
