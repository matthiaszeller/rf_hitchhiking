import argparse

from rf_hitchhike.schemas import RecordingMetadata

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file", type=str)
    args = p.parse_args()

    meta = RecordingMetadata.from_file(args.file)
    print(meta)
