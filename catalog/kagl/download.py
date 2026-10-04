"""Download shards of the Marqo/KAGL dataset (Kaggle Fashion Product Images) from Hugging Face."""

import argparse

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.hf_api import RepoFile

REPO_ID = "Marqo/KAGL"
# Pin the dataset to one commit so every run (and every experiment) sees identical files.
REVISION = "5146654f23da1f808a86370320cc8128c928f6f9"
NUM_SHARDS = 35


def shard_filename(index: int) -> str:
    """Path of one shard inside the repo, e.g. 0 -> 'data/data-00000-of-00035.parquet'."""
    return f"data/data-{index:05d}-of-{NUM_SHARDS:05d}.parquet"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--shards", type=int, nargs="+", required=True, help="shard indices, e.g. 0 11 22 33"
    )
    parser.add_argument("--dry-run", action="store_true", help="print sizes; download nothing")
    args = parser.parse_args()

    invalid = [i for i in args.shards if not 0 <= i < NUM_SHARDS]
    if invalid:
        parser.error(f"shard indices must be between 0 and {NUM_SHARDS - 1}; got {invalid}")
    shards = sorted(set(args.shards))
    filenames = [shard_filename(i) for i in shards]

    if args.dry_run:
        infos = HfApi().get_paths_info(REPO_ID, filenames, repo_type="dataset", revision=REVISION)
        files = [info for info in infos if isinstance(info, RepoFile)]
        for file in files:
            print(f"{file.path}: {file.size / 1e6:.1f} MB")
        print(f"Total: {sum(file.size for file in files) / 1e6:.1f} MB in {len(files)} files")
        return

    for name in filenames:
        path = hf_hub_download(REPO_ID, name, repo_type="dataset", revision=REVISION)
        print(path)


if __name__ == "__main__":
    main()
