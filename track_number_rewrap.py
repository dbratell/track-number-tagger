"""Program to renumber mp3 files so that their ID3 track number is below 100"""

import argparse
import os

import eyed3


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Rewrap disc and track numbers")
    parser.add_argument("directory")
    parser.add_argument("--reverse-disc-and-track", action="store_true",
                        help="MORON SANDISK SPORT PLUS")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    mp3_files:list[str] = os.listdir(args.directory) # type: ignore

    info:list[tuple[str,str,str,str,int,int]] = []
    for i, file_name in enumerate(mp3_files): # type: ignore
        assert isinstance(file_name, str)
        if not file_name.endswith(".mp3"):
            continue
        mp3 = eyed3.load(os.path.join(args.directory, file_name)) # type: ignore
        genre = str(mp3.tag.genre) # type: ignore
        album:str = mp3.tag.album # type: ignore
        title:str = mp3.tag.title # type: ignore
        disc = mp3.tag.disc_num.count # type: ignore
        if disc is None:
            disc = 0

        track:int = mp3.tag.track_num.count # type: ignore
        if track is None:
            track = 0

        assert isinstance(album, str)
        assert isinstance(title, str)
        assert isinstance(disc, int)
        assert isinstance(track, int)
        info.append((file_name, genre, album, title, disc, track))

    def sort_key(data:tuple[str,str,str,str,int,int]):
        return (data[4], data[5])

    ordered_info = sorted(info, key=sort_key)

    # Rewrap numbers
    last_original_disc_number = 1
    last_written_disc_number = 1
    for i in range(len(ordered_info)):
        file_name, genre, album, title, disc, track = ordered_info[i]
        if disc == 0:
            disc = 1

        # If the original data jumps to a new disc, so should we
        # and we cannot use the original disc numbers since they might
        # have been already used by rewrapping earlier discs.
        if disc != last_original_disc_number:
            last_original_disc_number = disc
            disc = last_written_disc_number + 1

        while track > 99:
            track -= 99
            disc += 1

        last_written_disc_number = disc

        ordered_info[i] = (file_name, genre, album, title, disc, track)


    for file_name, _genre, _album, _title, disc, track in ordered_info:
        mp3 = eyed3.load(os.path.join(args.directory, file_name)) # type: ignore

        if args.reverse_disc_and_track:
            # OPPOSITE SINCE SANDISK SPORT PLUS HAS A MORONIC SORTING
            # ALGORITHM
            mp3.tag.track_num = (disc, last_written_disc_number)
            mp3.tag.disc_num = track
        else:
            mp3.tag.track_num = track
            mp3.tag.disc_num = (disc, last_written_disc_number)

        if not args.dry_run:
            mp3.tag.save()
        else:
            print(f"Would write {file_name}: {disc}.{track}")

if __name__ == "__main__":
    main()
