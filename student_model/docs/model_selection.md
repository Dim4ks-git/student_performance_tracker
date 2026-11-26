# M02 Model selection decision

Make the prediction at the pre-exam check-in using observations available
before the exam starts. The target is `exam_score` in marks out of 100.
Use the following inputs in the order defined by [the feature schema](../preprocessing/feature_schema.json).

1. `previous_exam_score`
2. `attendance_percentage`
3. `study_hours_per_day`
4. `practice_tests_completed`
5. `exam_preparation_days` (whole days already spent preparing at check-in)
6. `exam_difficulty` (course-supplied `Easy`, `Medium`, or `Hard` available at check-in)

The bundled synthetic CSV simulates a course that announces difficulty in advance.
It contains no timestamps verifying when students learned that rating. For another
CSV, append the optional `exam_difficulty_known_before_exam` column to the standard
header. Set it to `true` only on rows with a confirmed advance rating. Missing flags,
`false`, and files without that column leave difficulty unknown. Supply preparation
days as of the check-in date, leaving the cell empty if unknown.

Group the train, validation, and final test splits by `student_id` so each
student belongs to one partition. Use `revision_frequency` and
`assignment_completion_rate` for coaching only. The synthetic generator uses
practice-test count in its score formula and samples revision frequency
separately. Exclude the post-exam fields `questions_attempted`,
`questions_correct`, `performance_grade`, `pass_status`, and
`performance_level`.

Median-impute and standardize numeric inputs using training data. One-hot encode
the three difficulty levels. An unknown difficulty contributes zero across all
three indicators. Fit `Ridge(alpha=1.0)` on the combined features. Compare the
result (`score_model`) against three baselines on the same validation rows.

- Predict the training median of `exam_score` for every row.
- Fit the same Ridge pipeline using only `previous_exam_score`.
- Fit the original four-input numeric Ridge model (`ridge4`) for a direct comparison.

Fit all preprocessing and models on training students for validation. Use
validation mean absolute error (MAE) for selection and record MAE and root mean
squared error (RMSE) in marks for all four methods.

Accept the score model for the synthetic-data demo when its validation MAE
is at least 1.0 mark lower than the better of the median and prior-mark baselines. Apply the
inclusive threshold to unrounded metrics. For example, if the better baseline
MAE is 11.0, a score-model MAE of 10.0 qualifies and 10.01 falls short. Use
untouched test students for final testing after selection. Require evidence from
later comparable exams with real students before making individual forecasts.

## Local training results

From the repository root, with the pinned Python environment active, create a
fresh run directory and use the checked-in CSV for validation and finalization.

```bash
mkdir -p student_model/runs
run_dir=$(mktemp -d student_model/runs/run.XXXXXXXX)
csv=student_model/datasets/student_exam_performance_copy.csv
python -m student_model.validate "$csv" > "$run_dir/validation.json" &&
  python -m student_model.finalize "$csv" "$run_dir/validation.json" "$run_dir/bundle"
```

Git ignores `student_model/runs/`. For a release, publish the verified `bundle/`
as one artifact so the fitted pipeline travels with its feature schema,
manifest, reference prediction, and metrics. Keep the rest of the run directory
local.

## Using the bundle in study_service

With the service dependencies installed, start the API from the repository root.

```bash
STUDY_MODEL_DIR="$run_dir/bundle" python -m uvicorn study_service.server:app
```

Send JSON to `POST /v1/study-check-ins`. Existing clients can omit the new fields.
Both four- and six-input bundles use the feature order in their saved schema.
For a course-announced difficulty, a first check-in can look like this.

```json
{
  "previous_exam_score": 73.4,
  "study_hours_per_day": 3.42,
  "practice_tests_completed": 10,
  "exam_preparation_days": 4,
  "exam_difficulty": "Easy",
  "exam_difficulty_known_before_exam": true,
  "goal": "remember_material",
  "study_method": "Self-Reading"
}
```

Leave the difficulty flag unset or false when the source or timing is uncertain.
Preparation days and attendance can also be omitted. Advice is available even if
there is too little information for a score.

The client keeps the previous goal locally and asks the student how the suggested
action went. Send that feedback on the next visit, for example:

```json
{
  "last_check_in": {"goal": "remember_material", "outcome": "did_not_help"}
}
```

Outcomes are `helped`, `did_not_help`, and `not_tried`. The service continues the
previous goal unless a new top-level `goal` is supplied. A changed goal starts a
fresh recommendation. Omitting the previous goal applies the feedback to the
current goal. Resend current score inputs to receive an estimate on a return visit.
