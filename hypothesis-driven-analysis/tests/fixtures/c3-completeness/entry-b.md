## Data Validity

- Source completeness semantics: in S2, absence of a row means "not yet closed as of the extract" (event pending, not event absent or export-dropped) — established by the closed-incident age benchmark above and by the fact that `incidents.csv` (S1) already lists these 11 incidents by ID with a real `opened_at`, so they are not missing rows, they are open ones. This licenses treating them as right-censored survivors, not as an unknown-direction missingness problem.
