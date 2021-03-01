# AutoPlayer

AutoPlayer - a simple cli app to keep track of your show watching progress.

Shows' progress is stored in `.auto_player` file in current working directory. I expect a user to be in show's directory that will cause saving state file there.

The app also can automate subtitles and audio-track injection when they are placed in some subdirectories where players don't look for them. Looks for optional keys in `add` command.

## Usage

```
Usage: auto-player [OPTIONS] COMMAND [ARGS]...

Options:
  --config TEXT   Path to config file
  --session TEXT  Session to use. Data in sessions are isolated
  --help          Show this message and exit.

Commands:
  add     Add show
  delete  Delete show
  edit    Edit show
  info    Show info about show
  list    List shows
  play    Play next episode in show
```

Just use `-h` key to see more help. I tried to make it as intuitive as possible.
