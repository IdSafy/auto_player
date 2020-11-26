from typing import Union, Any, Optional, Dict
import click
from click.core import Option, Parameter, Context

from file_group import FilesGroup
from show.statefull import StatefullShowWrapper
from backend.localfilebackend import LocalfileBackend
from player import Player
from auto_player import AutoPlayer

BACKENDS_CLASSES: Dict[str, type] = {
    LocalfileBackend.NAME: LocalfileBackend,
}

DEFAULT_SESSION = "default"

def abort_if_false(ctx: Context, _: Union[Option, Parameter], value: Any) -> Any:
    if not value:
        ctx.abort()

def print_files_group(files_group: Optional[FilesGroup], name: str) -> None:
    capitalized_name = name.capitalize()
    print(f"{capitalized_name} files:")
    if files_group is not None:
        directory = files_group.directory
        for path in files_group:
            relative_path = path.relative_to(directory)
            print(f"\t{relative_path}")
    else:
        print(None)
def print_show_info(show: StatefullShowWrapper) -> None:
    print(f"Name: {show.name}")
    print(f"Length: {len(show)}")
    print(f"Watched: {show.counter}")
    print_files_group(show.video_group, "video")
    print_files_group(show.audio_group, "audio")
    print_files_group(show.subtitles_group, "subtitles")

@click.group()
@click.option("--backend", "backend_name",
    default=LocalfileBackend.NAME,
    type=click.Choice(BACKENDS_CLASSES.keys()),
    help="Backend to use")
@click.option("--session", default=DEFAULT_SESSION,
    help="Session to use. Data in sessions are isolated")
@click.pass_context
def cli(context: Context, backend_name: str, session: str):
    backend_class = BACKENDS_CLASSES[backend_name]
    backend = backend_class(session=session)
    player = Player()
    context.obj = AutoPlayer(backend, player)

@cli.command(help="List show")
@click.pass_obj
def ls(obj: AutoPlayer):
    app = obj
    shows = app.list_shows()
    for number, show in zip(range(1, len(shows) + 1), shows):
        print(f"{number}. {show.name} [{show.counter}/{len(show)}]")

@cli.command(help="Show info about show")
@click.option('--full', is_flag=True, help="Show more info")
@click.argument("name_or_number",default = "1",required=False)
@click.pass_obj
def info(obj: AutoPlayer, full: bool, name_or_number: str):
    app = obj
    show = app.get_show(name_or_number)
    if show is None:
        print("Unknown show")
        return
    print_show_info(show)

@cli.command(help="Play next episode in show")
@click.option("-e", '--episode', default = -1,
    type=click.INT,
    help="Number of episode to play. Won't change state")
@click.option('--continuous', is_flag=True,
    help="Play next episode automatically")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def play(obj: AutoPlayer, continuous: bool, name_or_number: str, episode: int):
    app = obj
    app.play(name_or_number, episode)
    # raise Exception(" Not implemented")

@cli.command(help="Add show")
@click.option('--video_dir', default=".",
    help="video root directory")
@click.option('--video_regex', default=r".+\.(mkv|mp4)",
    help="Regex for video files")
@click.option('--audio_dir', default=".",
    help="audio root directory")
@click.option('--audio_regex', default=r".+\.(i don't remember audio resolutions)",
    help="Regex for audio files")
@click.option('--subtitles_dir', default=".",
    help="subtitles root directory")
@click.option('--subtitles_regex', default=r".+\.(ass|srt)",
    help="Regex for subtitles files")
@click.option('--watched', default=0,
    help="How many episodes you have already watched")
@click.option('--test', default=False, is_flag=True,
    help="Print finded files but not add to state")
@click.argument("name", required=True)
@click.pass_obj
def add(obj: AutoPlayer, test: bool, name: str, **kwargs):
    app = obj
    show = app.add_show(test=test, name=name, **kwargs)
    print_show_info(show)

@cli.command(help="Edit show")
@click.option('--video_dir', default=".",
    help="video root directory")
@click.option('--video_regex', default=r".+\.(mkv|mp4)",
    help="Regex for video files")
@click.option('--audio_dir', default=".",
    help="audio root directory")
@click.option('--audio_regex', default=r".+\.(i don't remember audio resolutions)",
    help="Regex for audio files")
@click.option('--subtitles_dir', default=".",
    help="subtitles root directory")
@click.option('--subtitles_regex', default=r".+\.(ass|srt)",
    help="Regex for subtitles files")
@click.option('--watched', default=0,
    help="How many episodes you have already watched")
@click.option('--test', default=False, is_flag=True,
    help="Print finded files but not add to state")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def edit(obj: AutoPlayer, name_or_number: str, test: bool, **kwargs):
    app = obj
    raise Exception(" Not implemented")

@cli.command(help="Delete show")
@click.argument("name_or_number", default = "1", required=False)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False, prompt='Are you sure you want to remove the show?')
@click.pass_obj
def delete(obj: AutoPlayer, name_or_number: str):
    app = obj
    app.delete_show(name_or_number)

if __name__ == "__main__":
    cli()
