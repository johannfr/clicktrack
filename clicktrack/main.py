import click
import sys, os
from pydub import AudioSegment


def float_range(start, stop, step):
    while start < stop:
        yield start
        start += step


def info(flag, message):
    if flag:
        sys.stdout.write(message)
        sys.stdout.flush()


PATH_TO_SELF = os.path.abspath(sys.argv[0])


@click.command()
@click.option("--bpm", default=120, help="Beats per minute")
@click.option(
    "--highclick",
    default=os.path.join(PATH_TO_SELF, "cowbell-high.wav"),
    type=click.Path(exists=True),
    help="Path to audio-file for high-pitched click",
)
@click.option(
    "--lowclick",
    default=os.path.join(PATH_TO_SELF, "cowbell-low.wav"),
    type=click.Path(exists=True),
    help="Path to audio-file for low-pitched click",
)
@click.option(
    "--countprefix",
    default=4,
    help="How meany measures to prefix with click",
    show_default=True,
)
@click.option("--division", default=4, help="Measure division", show_default=True)
@click.option(
    "--gain-track",
    default=6.0,
    type=float,
    help="Gain to apply to backing-track_padding",
    show_default=True,
)
@click.option(
    "--gain-click",
    default=-6.0,
    type=float,
    help="Gain to apply to click-audio",
    show_default=True,
)
@click.option(
    "--pan-track",
    default=-1.0,
    type=float,
    help="Pan for backing-track, -1.0 to 1.0",
    show_default=True,
)
@click.option(
    "--pan-click",
    default=1.0,
    type=float,
    help="Pan for click-track, -1.0 to 1.0",
    show_default=True,
)
@click.option(
    "--track-padding",
    default=10,
    type=int,
    help="Padding before backing-track (ms)",
    show_default=True,
)
@click.option("-v", "--verbose", is_flag=True)
@click.argument("backingtrack", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def main(
    backingtrack,
    output,
    bpm,
    highclick,
    lowclick,
    countprefix,
    division,
    gain_track,
    gain_click,
    pan_track,
    pan_click,
    track_padding,
    verbose,
):
    duration_beat = (60 * 1000) / bpm
    info(verbose, "Loading click-samples [{} dB]...".format(gain_click))
    click_high = AudioSegment.from_file(highclick) + gain_click
    click_low = AudioSegment.from_file(lowclick) + gain_click
    info(verbose, " Done\n")
    info(
        verbose,
        "Loading and processing backing-track [{}{} dB, {} ms padding]...".format(
            "+" if gain_track > 0 else "", gain_track, track_padding
        ),
    )
    total_padding = AudioSegment.silent(
        duration=track_padding + (duration_beat * division * countprefix)
    )
    track = (
        total_padding + AudioSegment.from_file(backingtrack).pan(pan_track)
    ) + gain_track
    info(verbose, " Done\n")

    # Generate an empty click-track
    info(verbose, "Generating click-track [{} BPM, {} div]...".format(bpm, division))
    click_track = AudioSegment.silent(duration=len(track))
    count = 0
    for i in float_range(0, len(track), duration_beat):
        click_track = click_track.overlay(
            click_high if count % division == 0 else click_low, position=round(i)
        )
        count += 1
    info(verbose, " Done\n")

    info(verbose, "Mixing...")
    mix = track.overlay(click_track.pan(pan_click))
    info(verbose, " Done\n")
    info(verbose, "Exporting to: {}...".format(output))
    mix.export(output, format="mp3")
    info(verbose, " Done\n")


if __name__ == "__main__":
    main()
