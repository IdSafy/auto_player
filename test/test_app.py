import json
import pytest

from auto_player.app import AutoPlayer, create_auto_player

@pytest.fixture
def config_file(tmpdir):
    path = tmpdir.join("config.json")
    config = {
        "backend": {
            "class": "auto_player.backend.localfilebackend.LocalfileBackend",
            "params": {},
        },
        "player": {
            "class": "auto_player.player.CunstuctorPlayer",
            "params": {
                "base": ["echo"],
                "video_file_wrapper": ["{episode.video_file}"],
                "audio_file_wrapper": ["{episode.audio_file}"],
                "subtitles_file_wrapper": ["{episode.subtitles_file}"],
                "appendix": [],
            },
        },
    }
    with open(path, "w") as file:
        json.dump(config, file)
    return path

def test_app_creation(config_file):
    app = create_auto_player(config_path=config_file)
    assert app is not None
    assert isinstance(app, AutoPlayer)