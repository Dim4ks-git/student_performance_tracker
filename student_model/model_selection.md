# M02 Model selection decision

Make the prediction at the pre-exam check-in using observations available
before the exam starts. The target is `exam_score` in marks out of 100.
Use the following inputs in the order defined by [the feature schema](feature_schema.json).

1. `previous_exam_score`
2. `attendance_percentage`
3. `study_hours_per_day`
4. `practice_tests_completed`

Group the train, validation, and final test splits by `student_id` so each
student belongs to one partition. Use `revision_frequency` and
`assignment_completion_rate` for coaching only. The synthetic generator uses
practice-test count in its score formula and samples revision frequency
separately. Exclude the post-exam fields `questions_attempted`,
`questions_correct`, `performance_grade`, `pass_status`, and
`performance_level`.

Use median imputation, then standardization, then `Ridge(alpha=1.0)`.
This gives a small CPU model for numeric inputs, with imputation for missing
values and scaling so the regularization acts on comparable feature scales.
Compare against two baselines on the same validation rows.

- Predict the training median of `exam_score` for every row.
- Fit the same Ridge pipeline using only `previous_exam_score`.

Fit all preprocessing and models on training students for validation. Use
validation mean absolute error (MAE) for selection and record MAE and root mean
squared error (RMSE) in marks for all three methods.

Accept the four-field model for the synthetic-data demo when its validation MAE
is at least 1.0 mark lower than the lower of the two baseline MAEs. Apply the
inclusive threshold to unrounded metrics. For example, if the better baseline
MAE is 11.0, a four-field MAE of 10.0 qualifies and 10.01 falls short. Use
untouched test students for final testing after selection. Require evidence from
later comparable exams with real students before making individual forecasts.
