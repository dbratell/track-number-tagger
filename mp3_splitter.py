"""Using ffmpeg, this splits an mp3 of m4b file into smaller chunks"""

import argparse
import os
import subprocess
import shutil

def locate_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        # Try some alternative paths.
        alt_paths: list[str] = []

        for root in (r"c:\Program Files",
                    r"c:\Program Files (x86)"):
            dirs = os.listdir(root)
            for directory in dirs:
                if "ffmpeg" in directory.lower():
                    alt_paths.append(os.path.join(root, directory))
                    alt_paths.append(os.path.join(root, directory, "bin"))

        ffmpeg = shutil.which("ffmpeg", path=os.pathsep.join(alt_paths))
        if ffmpeg is None:
            raise ValueError("Could not locate any ffmpeg binary. Searched path and some common locations.")
    return ffmpeg

def main():
    """Main function."""
    ffmpeg = locate_ffmpeg()

    parser = argparse.ArgumentParser(description="Sets disc and track numbers according to file names")
    parser.add_argument("--file", type=str, default="dummy", required=True)
    parser.add_argument("--destination", help="defaults to splitted_file in the same directory as file. "
                        "Will be created if it does not exist")
    parser.add_argument("--length", type=int, default=1200, help="Length in seconds for each part")
    parser.add_argument("--title", help="Base title for ID3")
    parser.add_argument("--force", action="store_true", help="Do the splitting even if the files are already there")

    args = parser.parse_args()

    audio_file = args.file

    exists = os.path.exists(audio_file)
    assert exists

    audio_file:str = args.file
    base_file_name = os.path.basename(audio_file)
    base_base, base_ext = os.path.splitext(base_file_name)

    assert args.length is not None
    assert args.length > 0

    if args.destination is None:
        destination = os.path.join(os.path.dirname(audio_file),
                                   "splitted_file")
    else:
        destination = args.destination

    # import track_number_lister
    # artist, album, title =  track_number_lister.get_artist_album_title(audio_file)
    # print(artist, album, title)

    first_generated_file = f"{base_base}_{1:03d}{base_ext}"
    if args.force or not os.path.isfile(os.path.join(destination, first_generated_file)):
        ffmpeg_command = [
            ffmpeg,
            "-i",
            audio_file,

            "-f",
            "segment",
            "-segment_time",
            str(args.length),
            "-segment_start_number",
            str(1),

            "-c",
            "copy",

            os.path.join(destination, f"{base_base}_%03d{base_ext}")
        ]

        os.makedirs(destination, exist_ok=True)
        subprocess.run(ffmpeg_command)
    else:
        print("Skipping splitting because there are already generated files there. Use --force to still split.")

    destination_files:list[str] = os.listdir(destination) # type: ignore
    a_file_list = sorted(
        x for x in destination_files if x.startswith(base_base + "_") and x.endswith(base_ext)
    )
    # Now set the title and # fields in each file
    highest_number = 0
    for number, file_part in enumerate(a_file_list, start=1):
        assert f"{number:03d}" in file_part, (file_part, number)
        highest_number = number

    temp_file = os.path.join(destination, f"temp{base_ext}")
    if args.title:
        title = args.title
    else:
        title = base_base.replace("_", " ")
    for number, file_part in enumerate(a_file_list, start=1):
        file_part_with_path = os.path.join(destination, file_part)
        ffmpeg_command_tag_command = [
            ffmpeg,
            "-i",
            file_part_with_path,

            "-c",
            "copy",

            "-metadata",
            f"title={number:03d} {title} ",

            "-metadata",
            f"track={number}/{highest_number}",

            "-id3v2_version",
            "3",
            "-write_id3v1",
            "1",

            temp_file
        ]

        subprocess.run(ffmpeg_command_tag_command)

        os.replace(temp_file, file_part_with_path)



    # import track_number_tagger
    # track_number_tagger.track_number_tagger(args.destination,
    #                                         artist=artist,
    #                                         album=album,
    #                                         title=title,
    #                                         rename_with_number=True,
    #                                         dry_run=False)


if __name__ == "__main__":
    main()
