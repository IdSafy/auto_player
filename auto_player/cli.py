import sys
from typing import Union, Any, Dict, TypeVar
import click
from click.core import Option, Parameter, Context

from .app import AutoPlayer, create_auto_player, DEFAULT_CONFIG_PATH, Error, Rezult

DEFAULT_SESSION = "default"

def abort_if_false(ctx: Context, _: Union[Option, Parameter], value: Any) -> Any:
    if not value:
        ctx.abort()

def print_files_group(files_group_info: Dict[str, Any], name: str) -> None:
    capitalized_name = name.capitalize()
    print(f"{capitalized_name} files:")
    print(f"\tClass: {files_group_info['class'].__name__}")

    print("\tFiles (may be generated):")
    if len(files_group_info["files"]) == 0:
        print("\t\tNone")
    for file_info in files_group_info["files"]:
        print(f"\t\t{file_info['relative_path']}")

def print_show_info(show_info: Dict[str, Any]) -> None:
    print(f"Name: {show_info['name']}")
    print(f"Length: {show_info['length']}")
    print(f"Watched: {show_info['watched']}")
    print_files_group(show_info['video_group'], "video")
    print_files_group(show_info['audio_group'], "audio")
    print_files_group(show_info['subtitles_group'], "subtitles")

T = TypeVar('T')
def command_rezult_handler(rezult: Rezult[T]) -> T:
    if isinstance(rezult, Error):
        print("Error:", rezult.msg)
        sys.exit(1)
    return rezult

@click.group()
@click.option("--config", "config_path",
    default=DEFAULT_CONFIG_PATH,
    help="Path to config file")
@click.option("--session", default=DEFAULT_SESSION,
    help="Session to use. Data in sessions are isolated")
@click.pass_context
def cli(context: Context, config_path: str, session: str):
    context.obj = create_auto_player(config_path=config_path, session=session)

@cli.command("list", help="List shows")
@click.pass_obj
def list_command(obj: AutoPlayer):
    app = obj
    shows = app.list_shows()
    for number, show in zip(range(1, len(shows) + 1), shows):
        print(f"{number}. {show.name} [{show.counter}/{len(show)}]")

@cli.command("info", help="Show info about show")
@click.option('--full', is_flag=True, help="Show more info")
@click.argument("name_or_number",default = "1",required=False)
@click.pass_obj
def info_command(obj: AutoPlayer, full: bool, name_or_number: str):
    app = obj
    show = command_rezult_handler(app.get_show(name_or_number))
    info = command_rezult_handler(show.info())
    print_show_info(info)

@cli.command("play", help="Play next episode in show")
@click.option("-e", '--episode', default = -1,
    type=click.INT,
    help="Number of episode to play. Won't change state")
@click.option('--continuous', is_flag=True,
    help="Play next episode automatically")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def play_command(obj: AutoPlayer, continuous: bool, name_or_number: str, episode: int):
    app = obj
    show = command_rezult_handler(app.get_show(name_or_number))
    command_rezult_handler(show.play(episode))

@cli.command("add", help="Add show")
@click.option('-v', '--video_dir', "--vd", default=".",
    help="video root directory")
@click.option('--video_regex', "--vx", default=r".+\.(mkv|mp4)",
    help="Regex for video files")
@click.option('-a', '--audio_dir', "--ad", default=".",
    help="audio root directory")
@click.option('--audio_regex', "--ax", default=r".+\.(i don't remember audio resolutions)",
    help="Regex for audio files")
@click.option('-s', '--subtitles_dir', "--sd", default=".",
    help="subtitles root directory")
@click.option('--subtitles_regex', "--sx", default=r".+\.(ass|srt)",
    help="Regex for subtitles files")
@click.option("-w", '--watched', default=0,
    help="How many episodes you have already watched")
@click.option('-t', '--test', default=False, is_flag=True,
    help="Print finded files but not add to state")
@click.argument("name", required=True)
@click.pass_obj
def add_command(obj: AutoPlayer, test: bool, name: str, **kwargs):
    app = obj
    rezult = app.add_show(test=test, name=name, **kwargs)
    show = command_rezult_handler(rezult)
    info = command_rezult_handler(show.info())
    print_show_info(info)

@cli.command("edit", help="Edit show")
@@click.option('-v', '--video_dir', "--vd", default=".",
    help="video root directory")
@click.option('--video_regex', "--vx", default=r".+\.(mkv|mp4)",
    help="Regex for video files")
@click.option('-a', '--audio_dir', "--ad", default=".",
    help="audio root directory")
@click.option('--audio_regex', "--ax", default=r".+\.(i don't remember audio resolutions)",
    help="Regex for audio files")
@click.option('-s', '--subtitles_dir', "--sd", default=".",
    help="subtitles root directory")
@click.option('--subtitles_regex', "--sx", default=r".+\.(ass|srt)",
    help="Regex for subtitles files")
@click.option("-w", '--watched', default=0,
    help="How many episodes you have already watched")
@click.option('-t', '--test', default=False, is_flag=True,
    help="Print finded files but not add to state")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def edit_command(obj: AutoPlayer, name_or_number: str, test: bool, **kwargs):
    app = obj
    raise Exception(" Not implemented")

@cli.command("delete", help="Delete show")
@click.argument("name_or_number", default = "1", required=False)
@click.option('--yes', is_flag=True, callback=abort_if_false, expose_value=False, prompt='Are you sure you want to remove the show?')
@click.pass_obj
def delete_command(obj: AutoPlayer, name_or_number: str):
    app = obj
    show = command_rezult_handler(app.get_show(name_or_number))
    show.delete()

if __name__ == "__main__":
    cli()
