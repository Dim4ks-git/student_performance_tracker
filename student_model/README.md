# Student score model

This Python package validates and trains a pre-exam score model on the bundled
synthetic dataset. It publishes a fitted model with its schema, evaluation
metrics, manifest, and a reference prediction.

## Where to look

| Path | What belongs here |
| --- | --- |
| [validate.py](validate.py) | Score candidate models on validation students and write a validation receipt. |
| [finalize.py](finalize.py) | Check the receipt, evaluate on held-out students, and publish the bundle. |
| [preprocessing/](preprocessing/) | CSV parsing, numeric validation, student-group splits, and input loading. The [feature schema](preprocessing/feature_schema.json) defines the target and feature order. |
| [modeling/](modeling/) | Estimators, error metrics, and final evaluation. |
| [publishing/](publishing/) | Save and verify the fitted pipeline, then write the manifest and metrics. |
| [datasets/](datasets/) | Checked-in synthetic exam dataset used for training and integration tests. |
| [tests/](tests/) | Unit and integration tests for the training workflow. |
| [docs/](docs/) | [Model selection criteria and training commands](docs/model_selection.md). |
| `runs/` | Git-ignored output from local training runs. |

## Setup and tests

From the repository root (the directory containing `student_model/`), activate
a Python environment and install the pinned [dependencies](requirements.txt).

```bash
python -m pip install -r student_model/requirements.txt
python -m unittest discover -s student_model/tests
```
