"""Program to set track numbers on mp3 files making up an audio book, to make
sure they are played in the right order."""

import argparse
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

    args = parser.parse_args()

    mp3_files = os.listdir(args.directory)

    mp3_files_in_order = filter_and_order(args.directory, mp3_files)
    disc_nums = []
    for file_name in mp3_files_in_order:
        name_without_ext = file_name[:-4]
        parts = split_in_strings_and_numbers(name_without_ext)
        if (len(parts) > 1 and
                isinstance(parts[-1], int) and
                isinstance(parts[-2], int)):
            # Add this disc number to the list so that we can later
            # see what was the highest disc number we saw.
            disc_nums.append(parts[-2])

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

        if (len(parts) > 1 and
                isinstance(parts[-1], int) and
                isinstance(parts[-2], int)):
            track_number = parts[-1]
            disc_number = (parts[-2], max(disc_nums))
        else:
            disc_number = 0
            track_number = i + 1
            assert False, repr(parts)
        print("#%d.%d\t%s" % (disc_number[0], track_number, file_name))
        if args.reverse_disc_and_track:
            # OPPOSITE SINCE SANDISK SPORT PLUS HAS A MORONIC SORTING
            # ALGORITHM
            mp3.tag.track_num = disc_number
            mp3.tag.disc_num = track_number
        else:
            mp3.tag.track_num = track_number
            mp3.tag.disc_num = disc_number

        if not args.dry_run:
            mp3.tag.save()
            if args.rename_with_number and file_name != mp3.tag.title + ".mp3":
                os.rename(os.path.join(args.directory, file_name),
                          os.path.join(args.directory, mp3.tag.title + ".mp3"))
#        else:
#            print(mp3.get_tags())

if __name__ == "__main__":
    main()
