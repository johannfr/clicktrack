import click
from pydub import AudioSegment
from pydub.playback import play


@click.command()
@click.option("--bpm", default=120, help="BeatsPerMinute")
@click.option("--highclick", default="cowbell-high.wav", type=click.Path(exists=True))
@click.option("--lowclick", default="cowbell-low.wav", type=click.Path(exists=True))
@click.option(
    "--countprefix", default=4, help="How meany measures to prefix with click"
)
@click.option("--division", default=4, help="Measure division")
@click.argument("backingtrack", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def main(backingtrack, output, bpm, highclick, lowclick, countprefix, division):
    duration_beat = (60 * 1000) / bpm
    click_high = AudioSegment.from_file(highclick) - 6.0
    click_high_padding = AudioSegment.silent(duration=duration_beat - len(click_high))
    click_low = AudioSegment.from_file(lowclick) - 6.0
    click_low_padding = AudioSegment.silent(duration=duration_beat - len(click_low))
    click_measure = (
        click_high
        + click_high_padding
        + ((click_low + click_low_padding) * (division - 1))
    ).pan(1.0)
    track_padding = AudioSegment.silent(duration=duration_beat * division * countprefix)
    track = (track_padding + AudioSegment.from_file(backingtrack).pan(-1.0)) + 6.0
    mix = track.overlay(click_measure, loop=True)
    mix.export(output, format="mp3")


if __name__ == "__main__":
    main()
