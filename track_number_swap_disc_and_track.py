"""Sansa Disk Plus mixes up track and disc and will sort things wrong. Swapping them helps."""

import argparse
import os

import eyed3 # type: ignore


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Swap disc and track numbers")
    parser.add_argument("directory")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    mp3_files:list[str] = os.listdir(args.directory) # type: ignore

    for i, file_name in enumerate(mp3_files): # type: ignore
        assert isinstance(file_name, str)
        if not file_name.endswith(".mp3"):
            continue
        mp3 = eyed3.load(os.path.join(args.directory, file_name)) # type: ignore
        disc = mp3.tag.disc_num.count # type: ignore
        if disc is None:
            disc = 0

        track:int = mp3.tag.track_num.count # type: ignore
        if track is None:
            track = 0

        assert isinstance(disc, int)
        assert isinstance(track, int)

        mp3.tag.track_num = disc # type: ignore
        mp3.tag.disc_num = track # type: ignore

        if not args.dry_run:
            mp3.tag.save() # type: ignore
        else:
            print(f"Would write {file_name}: {mp3.tag.disc_num.count}.{mp3.tag.track_num.count}")


if __name__ == "__main__":
    main()
