import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from .modeling.final_eval import final_evaluation
from .preprocessing.experiment import load_input
from .publishing.artifacts import save_model, write_manifest
from .publishing.reporting import write_metrics


def publish(csv_path, receipt_path, output_dir) -> Path:
    """Evaluate and publish a complete bundle with a single directory rename."""
    output = Path(output_dir)
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Output already exists: {output}")
    if not output.parent.is_dir():
        raise NotADirectoryError(f"Output parent must be an existing directory: {output.parent}")

    with Path(receipt_path).open(encoding="utf-8") as stream:
        receipt = json.load(stream)
    if not isinstance(receipt, dict):
        raise ValueError("Validation receipt must be a JSON object.")

    run = load_input(csv_path)
    pipeline, test_metrics, slices = final_evaluation(run, receipt)
    with TemporaryDirectory(prefix=".finalize-", dir=output.parent) as staging:
        bundle = Path(staging) / "bundle"
        bundle.mkdir()
        save_model(bundle, pipeline, run["schema"], run["dataset_sha256"])
        write_manifest(bundle, run)
        write_metrics(bundle, receipt, test_metrics, slices)
        if output.exists() or output.is_symlink():
            raise FileExistsError(f"Output already exists: {output}")
        bundle.rename(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a complete student model training run.")
    parser.add_argument("csv_path", help="Path to the input CSV")
    parser.add_argument("receipt_path", help="Path to the validation receipt JSON")
    parser.add_argument("output_dir", help="New bundle directory under an existing parent")
    args = parser.parse_args()
    try:
        output = publish(args.csv_path, args.receipt_path, args.output_dir)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{parser.prog}: {error}\n")
    print(output)


if __name__ == "__main__":
    main()
