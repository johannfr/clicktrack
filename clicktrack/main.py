import click
from pydub import AudioSegment
from pydub.playback import play


@click.command()
@click.option("--bpm", default=120, help="BeatsPerMinute")
@click.option(
    "--highclick",
    default="cowbell-high.wav",
    type=click.Path(exists=True),
    help="Path to audio-file for high-pitched click",
)
@click.option(
    "--lowclick",
    default="cowbell-low.wav",
    type=click.Path(exists=True),
    help="Path to audio-file for low-pitched click",
)
@click.option(
    "--countprefix", default=4, help="How meany measures to prefix with click"
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
):
    duration_beat = (60 * 1000) / bpm
    click_high = AudioSegment.from_file(highclick) + gain_click
    click_high_padding = AudioSegment.silent(duration=duration_beat - len(click_high))
    click_low = AudioSegment.from_file(lowclick) + gain_click
    click_low_padding = AudioSegment.silent(duration=duration_beat - len(click_low))
    click_measure = (
        click_high
        + click_high_padding
        + ((click_low + click_low_padding) * (division - 1))
    ).pan(pan_click)
    track_padding = AudioSegment.silent(duration=duration_beat * division * countprefix)
    track = (
        track_padding + AudioSegment.from_file(backingtrack).pan(pan_track)
    ) + gain_track
    mix = track.overlay(click_measure, loop=True)
    mix.export(output, format="mp3")


if __name__ == "__main__":
    main()
