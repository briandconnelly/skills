#!/usr/bin/env bash
# validate-result.sh < result.md
# Checks the child's .result against the R5.6 contract and prints one JSON object:
#   {"schema_valid": bool, "schema_errors": [..], "diff_unavailable": bool}
# Exit status is always 0: validity is data for run-child.sh (R5.7), not a failure of this script.
set -euo pipefail

awk '
BEGIN {
  want[1]="Summary"; want[2]="Critical"; want[3]="Important"; want[4]="Suggestions"; want[5]="Strengths"; want[6]="Not reviewed"
  n=0; cur=""; nerr=0; du=0; seen_text_before=0
  finding_re = "^- [^ ]+:[0-9]+ — (correctness|silent-failure|tests|comments) — .+ — .+$"
}
function err(m) { errs[++nerr]=m }
/^## / {
  name=substr($0,4); n++
  if (n<=6 && name!=want[n]) err("heading " n " is \"" name "\", expected \"" want[n] "\"")
  if (n>6) err("extra heading \"" name "\"")
  cur=name; body[cur]=""; next
}
{
  if (n==0) { if ($0 !~ /^[[:space:]]*$/) seen_text_before=1; next }
  body[cur]=body[cur] $0 "\n"
}
END {
  if (n<6) err("only " n " of 6 headings present")
  if (seen_text_before) err("text before ## Summary")
  # Summary: non-empty prose
  if (n>=1 && body["Summary"] ~ /^[[:space:]]*$/) err("Summary is empty")
  # Findings sections: (none) or finding bullets only
  split("Critical Important Suggestions", fs, " ")
  for (i=1;i<=3;i++) check_section(fs[i], 1)
  check_section("Strengths", 0)
  check_section("Not reviewed", 0)
  # Sentinel: first bullet of Not reviewed, nowhere else
  nr=body["Not reviewed"]; nl=split(nr, lines, "\n"); first=""
  for (i=1;i<=nl;i++) if (lines[i] !~ /^[[:space:]]*$/) { first=lines[i]; break }
  if (first ~ /^- DIFF-UNAVAILABLE: ./) du=1
  for (k in body) {
    if (k=="Not reviewed") { rest=nr; sub(/^[[:space:]]*- DIFF-UNAVAILABLE: [^\n]*\n?/, "", rest); if (rest ~ /DIFF-UNAVAILABLE/) err("sentinel appears more than once or not first in Not reviewed") }
    else if (body[k] ~ /DIFF-UNAVAILABLE/) err("sentinel outside Not reviewed: " k)
  }
  printf "{\"schema_valid\":%s,\"schema_errors\":[", (nerr==0 ? "true" : "false")
  for (i=1;i<=nerr;i++) { gsub(/"/, "\\\"", errs[i]); printf "%s\"%s\"", (i>1?",":""), errs[i] }
  printf "],\"diff_unavailable\":%s}\n", (du ? "true" : "false")
}
function check_section(name, findings,   b, L, i, m, nonblank) {
  if (!(name in body)) return
  b=body[name]; m=split(b, L, "\n"); nonblank=0
  for (i=1;i<=m;i++) {
    if (L[i] ~ /^[[:space:]]*$/) continue
    nonblank++
    if (L[i]=="(none)") { if (nonblank>1) err(name ": (none) mixed with other lines"); continue }
    if (L[i] !~ /^- /) { err(name ": line is neither (none) nor a bullet: " substr(L[i],1,40)); continue }
    if (findings && L[i] !~ finding_re && L[i] !~ /^- DIFF-UNAVAILABLE:/) err(name ": bullet is not \"- path:line — lens — sentence — why\": " substr(L[i],1,60))
  }
  if (nonblank==0) err(name ": empty section")
}
'
