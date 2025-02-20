"""Lists file by disc and track number"""

import argparse
import math
import os
import re

import eyed3

def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--reverse-disc-and-track", action="store_true",
                        help="MORON SANDISK SPORT PLUS")

    args = parser.parse_args()

    files:list[str] = os.listdir(args.directory) # type:ignore

    info:list[tuple[str,str,str,str,int|None,int|None,int|None,int|None]] = []
    for file_name in files:
        assert isinstance(file_name, str)
        if not file_name.endswith(".mp3"):
            continue
        mp3 = eyed3.load(os.path.join(args.directory, file_name)) # type: ignore
        if mp3 is None:
            print(f"Unsupported file format {file_name}")
            continue
        genre = str(mp3.tag.genre) # type: ignore
        album:str = mp3.tag.album # type: ignore
        title:str = mp3.tag.title # type: ignore
        disc:int|None = mp3.tag.disc_num.count # type: ignore
        disc_max:int|None = mp3.tag.disc_num.total # type: ignore
        # if disc is None:
        #     disc = 0

        track:int|None = mp3.tag.track_num.count # type: ignore
        track_max:int|None = mp3.tag.track_num.total # type: ignore
        # if track is None:
        #     track = 0

        assert isinstance(album, str)
        assert isinstance(title, str)
        assert disc is None or isinstance(disc, int)
        assert track is None or isinstance(track, int)
        assert disc_max is None or isinstance(disc_max, int)
        assert track_max is None or isinstance(track_max, int)
        info.append((file_name, genre, album, title, disc, disc_max, track, track_max))
    def sort_key(data:tuple[str,str,str,str,int|None,int|None,int|None,int|None]):
        if args.reverse_disc_and_track:
            return (data[6], data[4])
        return (data[4], data[6])

    for file_name, genre, album, title, disc, disc_max, track, track_max in sorted(info, key=sort_key):
        print(f"{file_name:<30}\t{genre:<10}\t{album:<10}\t{title:<10}\t{disc}/{disc_max} . {track}/{track_max}")


if __name__ == "__main__":
    main()
