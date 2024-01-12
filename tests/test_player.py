import pytest

from auto_player.player import CunstuctorPlayer
from auto_player.show import EpisodeSet


@pytest.fixture
def dummy_constructor_player() -> CunstuctorPlayer:
    player = CunstuctorPlayer(
        base=["kek_exec"],
        video_file_wrapper=["{episode.video_file}"],
        audio_file_wrapper=["/dub", "{episode.audio_file}"],
        subtitles_file_wrapper=["/sub", "{episode.subtitles_file}"],
    )
    return player


@pytest.fixture
def full_episode_set() -> EpisodeSet:
    return EpisodeSet(
        video_file="video_file",
        audio_file="audio_file",
        subtitles_file="subtitles_file",
    )


@pytest.fixture
def episode_set_without_audio(full_episode_set) -> EpisodeSet:
    return EpisodeSet(video_file="video_file", subtitles_file="subtitles_file")


@pytest.fixture
def episode_set_without_subtitles() -> EpisodeSet:
    return EpisodeSet(video_file="video_file", audio_file="audio_file")


def test_constructor_player_on_full_episode(dummy_constructor_player, full_episode_set):
    constructed_command = dummy_constructor_player._construct_command(full_episode_set)
    assert constructed_command == [
        "kek_exec",
        "video_file",
        "/dub",
        "audio_file",
        "/sub",
        "subtitles_file",
    ]


def test_constructor_player_on_not_full_episode(
    dummy_constructor_player, episode_set_without_audio, episode_set_without_subtitles
):
    constructed_command = dummy_constructor_player._construct_command(
        episode_set_without_audio
    )
    assert constructed_command == ["kek_exec", "video_file", "/sub", "subtitles_file"]

    constructed_command = dummy_constructor_player._construct_command(
        episode_set_without_subtitles
    )
    assert constructed_command == ["kek_exec", "video_file", "/dub", "audio_file"]
