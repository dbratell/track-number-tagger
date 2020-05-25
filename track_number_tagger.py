"""Program to set track numbers on mp3 files making up an audio book, to make
sure they are played in the right order."""

import argparse
import math
import os
import re

import eyed3

# There is also a library "mp3_tagger" that unfortunately badly
# corrupted the ID3 blocks with seemingly random binary content.

def split_in_strings_and_numbers(filename):
    """For sorting strings where numbers are sorted numerically rather
       than lexically."""
    res = []
    parts = re.split(r"[ _\.-]", filename)
    for part in parts:
        try:
            if part.startswith("D") and len(part) > 1 and part[1] in "0123456789":
                # Disk prefix?
                number = int(part[1:], 10)
                res.append("D")
            else:
                number = int(part, 10)
            res.append(number)
        except ValueError:
            res.append(part)

    return tuple(res)


def filter_and_order(directory, file_list):
    """Returns a list of mp3 files in the order they should be listened to
    according to the numbers in the file names."""
    file_list = [x for x in file_list
                 if x.endswith(".mp3") and
                 os.path.isfile(os.path.join(directory, x))]

    return sorted(file_list, key=split_in_strings_and_numbers)

def extract_disc_and_track_number_from_split_name(parts, default_track_number):
    """Given a file name split into strings and numbers, guess a track
    number and a disc number."""

    disc_number = 1
    track_number = default_track_number
    if (len(parts) > 2 and
            isinstance(parts[-1], int) and
            isinstance(parts[-2], int) and
            isinstance(parts[-3], int)):
        # Assume disc, track, total_tracks_on_disk
        track_number = parts[-2]
        disc_number = parts[-3]
    elif (len(parts) > 1 and
          isinstance(parts[-1], int) and
          isinstance(parts[-2], int)):
        track_number = parts[-1]
        disc_number = parts[-2]

    return (disc_number, track_number)

def recompute_disc_and_track_to_keep_under_limits(
        disc_number, track_number,
        max_track_number, highest_allowed_track_number):
    """Some readers don't like high track numbers. This makes sure track
    numbers stay below limits."""
    # Higher track numbers than 127 seems to sometimes cause problems?
    split_factor = 1
    if max_track_number > highest_allowed_track_number:
        # args.max_track_number numbers between 1 and
        # args.max_track_number
        split_factor = math.ceil(max_track_number /
                                 highest_allowed_track_number)

    if split_factor != 1:
        disc_number = ((disc_number - 1) * split_factor +
                       math.floor((track_number - 1) /
                                  highest_allowed_track_number) + 1)
        track_number = ((track_number - 1) % highest_allowed_track_number) + 1

    return (disc_number, track_number)


def main():
    """Main function."""
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    parser.add_argument("--reverse-disc-and-track", action="store_true",
                        help="MORON SANDISK SPORT PLUS")
    parser.add_argument("--rename-with-number", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--artist")
    parser.add_argument("--album")
    parser.add_argument("--title")
    parser.add_argument("--max-track-number", default=127, type=int)

    args = parser.parse_args()

    mp3_files = os.listdir(args.directory)

    mp3_files_in_order = filter_and_order(args.directory, mp3_files)
    max_disc_number = 1
    max_track_number = 1
    for i, file_name in enumerate(mp3_files_in_order):
        name_without_ext = file_name[:-4]
        parts = split_in_strings_and_numbers(name_without_ext)
        # Add this disc number to the list so that we can later
        # see what was the highest disc number we saw.
        (disc_number,
         track_number) = extract_disc_and_track_number_from_split_name(parts,
                                                                       i + 1)
        max_disc_number = max(disc_number, max_disc_number)
        max_track_number = max(track_number, max_track_number)

    for i, file_name in enumerate(mp3_files_in_order):
        mp3 = eyed3.load(os.path.join(args.directory, file_name))
        name_without_ext = file_name[:-4]
        parts = split_in_strings_and_numbers(name_without_ext)
        if args.album:
            mp3.tag.album = args.album
        if args.artist:
            mp3.tag.artist = args.artist
        mp3.tag.genre = "Audiobook"
        if args.title:
            mp3.tag.title = "%03d - %s" % ((i + 1), args.title)

        (disc_number,
         track_number) = extract_disc_and_track_number_from_split_name(parts,
                                                                       i + 1)

        (disc_number,
         track_number) = recompute_disc_and_track_to_keep_under_limits(
             disc_number, track_number,
             max_track_number, args.max_track_number)

        new_file_name = mp3.tag.title + ".mp3"
        print("#%d.%d\t%s" % (disc_number, track_number, file_name), end="")
        if args.rename_with_number and file_name != new_file_name:
            print("\t->\t%s" % new_file_name)
        else:
            print()

        if args.reverse_disc_and_track:
            # OPPOSITE SINCE SANDISK SPORT PLUS HAS A MORONIC SORTING
            # ALGORITHM
            mp3.tag.track_num = (disc_number, max_disc_number)
            mp3.tag.disc_num = track_number
        else:
            mp3.tag.track_num = track_number
            mp3.tag.disc_num = (disc_number, max_disc_number)

        if not args.dry_run:
            mp3.tag.save()
            if args.rename_with_number and file_name != new_file_name:
                os.rename(os.path.join(args.directory, file_name),
                          os.path.join(args.directory, new_file_name))
#        else:
#            print(mp3.get_tags())

if __name__ == "__main__":
    main()
