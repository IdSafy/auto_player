import os
import re
import pickle
import subprocess
from typing import Union, Pattern, Iterator, List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field

import click

from file_group import FilesGroupType, FilesGroup
from file_group.RegexFileGroup import RegexFileGroup
from show import Show, EpisodeSet
from show.statefull import StatefullShowWrapper
from backend import Backend
from backend.localfilebackend import LocalfileBackend
from state import State
from player import Player, PlayStatus
DEFAULT_SESSION = "default"

BACKENDS_CLASSES: Dict[str, type] = {
    LocalfileBackend.NAME: LocalfileBackend,
}

def print_context_info(context: Dict[str, Any]) -> None:
    backend = context["backend"]
    session = context["session"]
    print(f"Backend: {backend.NAME}")
    print(f"Session: {session}")
    print()

class AutoPlayer:
    def __init__(self, backend: Backend, player: Player):
        self.backend = backend
        self.player = player
        self.state = backend.load()

    def play(self, name_or_number: str, episode_number: int = -1, correct_zero: bool = True) -> None:
        if correct_zero:
            corrected_episode_number = episode_number - 1
        show = self.get_show(name_or_number)
        if show is None:
            raise Exception("Unknown show")
        episode_set = show.next_episode() if episode_number == -1 else show[corrected_episode_number]
        status = self.player.play(episode_set)
        if status.return_code == 0:
            self.backend.save(self.state)

    def list_shows(self) -> List[StatefullShowWrapper]:
        return self.state.shows

    def get_show(self, name_or_number: str) -> Optional[StatefullShowWrapper]:
        try:
            number = int(name_or_number)
        except Exception as e:
            number = -1
        if number > 0:
            return self.state.get_show_by_number(number)
        else:
            name = name_or_number
            return self.state.get_show_by_name(name)

    def add_show(self, name: str, **kwargs) -> None:
        pass

    def modify_show(self, name_or_number: str, **kwargs) -> None:
        pass

    def delete_show(self, name_or_number: str) -> None:
        show = self.get_show(name_or_number)
        if show is None:
            raise Exception("Unknown show")
        self.state.shows.remove(show)
        self.backend.save(self.state)

    def get_show_info(self, name_or_number: str) -> Dict[str, Any]:
        pass

def abort_if_false(ctx: click.core.Context, param: click.core.Option, value: bool) -> None:
    if not value:
        ctx.abort()

@click.group()
@click.option("--backend", "backend_name", default=LocalfileBackend.NAME, type=click.Choice(BACKENDS_CLASSES.keys()), help="Backend to use")
@click.option("--session", default=DEFAULT_SESSION, help="Session to use. Data in sessions are isolated")
@click.pass_context
def cli(context: click.core.Context, backend_name: str, session: str):
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
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def info(obj: AutoPlayer, full: bool, name_or_number: str):
    app = obj
    show = app.get_show(name_or_number)
    if show is None:
        print("Unknown show")
        return
    def print_files_group(files_group: FilesGroup, name: str) -> None:
        capitalized_name = name.capitalize()
        print(f"{capitalized_name} files:")
        if files_group is not None:
            directory = files_group.directory
            for path in files_group:
                relative_path = path.relative_to(directory)
                print(f"\t{relative_path}")
        else:
            print(None)
        
    print(f"Name: {show.name}")
    print(f"Length: {len(show)}")
    print(f"Watched: {show.counter}")
    print_files_group(show.video_group, "video")
    print_files_group(show.audio_group, "audio")
    print_files_group(show.subtitles_group, "subtitles")

@cli.command(help="Play next episode in show")
@click.option("-e", '--episode', default = -1, type=click.INT, help="Number of episode to play. Won't change state")
@click.option('--continuous', is_flag=True, help="Play next episode automatically")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def play(obj: AutoPlayer, continuous: bool, name_or_number: str, episode: int):
    app = obj
    app.play(name_or_number, episode)
    # raise Exception(" Not implemented")

@cli.command(help="Add show")
@click.option('--video_dir', default=".", help="video root directory")
@click.option('--video_regex', default=r".+\.(mkv|mp4)", help="Regex for video files")
@click.option('--audio_dir', default=".", help="audio root directory")
@click.option('--audio_regex', default=r".+\.(i don't remember audio resolutions)", help="Regex for audio files")
@click.option('--subtitles_dir', default=".", help="subtitles root directory")
@click.option('--subtitles_regex', default=r".+\.(ass|srt)", help="Regex for subtitles files")
@click.option('--watched', default=0, help="How many episodes you have already watched")
@click.argument("name", required=True)
@click.pass_obj
def add(obj: AutoPlayer, name: str, **kwargs):
    app = obj
    raise Exception(" Not implemented")

@cli.command(help="Edit show")
@click.option('--video_dir', default=".", help="video root directory")
@click.option('--video_regex', default=r".+\.(mkv|mp4)", help="Regex for video files")
@click.option('--audio_dir', default=".", help="audio root directory")
@click.option('--audio_regex', default=r".+\.(i don't remember audio resolutions)", help="Regex for audio files")
@click.option('--subtitles_dir', default=".", help="subtitles root directory")
@click.option('--subtitles_regex', default=r".+\.(ass|srt)", help="Regex for subtitles files")
@click.option('--watched', default=0, help="How many episodes you have already watched")
@click.argument("name_or_number", default = "1", required=False)
@click.pass_obj
def edit(obj: AutoPlayer, name_or_number: str, **kwargs):
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
