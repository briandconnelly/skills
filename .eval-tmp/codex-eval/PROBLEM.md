# Incident automation rollout review

I need a decision memo for Monday's operations review on whether we should expand the Assist workflow to the rest of the company.

We enabled Assist for both pilot service groups at 00:00 UTC on June 8 after one week on the manual workflow.

There was no holdout because the service owners wanted a single cutover, but they regard the before-and-after comparison as clean because every pilot incident followed the workflow active when it opened.

The dashboard team reports that median time to close fell materially in the Assist week, and Finance has translated that headline into responder-hours saved.

They want to book the savings in the rollout plan, while a few responders are saying the new workflow creates extra work on the incidents that are genuinely difficult.

Please determine whether Assist caused faster recovery, estimate how many responder-hours we can credibly attribute to it, and recommend whether the evidence supports expansion.

Do the analysis rather than accepting either team's interpretation.

The frozen local exports are in this directory:

- `incidents.csv` contains every incident opened from June 1 through June 14.
- `activity.csv` contains the recorded resolution activity as of the extract.
- `staffing.csv` contains the daily operating snapshot for each service group.

The extract was taken at 23:59 UTC on June 22, so even the newest incidents had at least seven full days to mature.

Use time to close and responder minutes as the primary outcomes, but check whether the recommendation is consistent with the other fields.

Leadership needs the result today, so work from these local exports only and state clearly what the data can and cannot establish.
