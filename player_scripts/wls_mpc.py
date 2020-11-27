#!/usr/bin/env python3

import os
import sys
import subprocess

def posix_path_to_windows_path(posix_path):
	if posix_path.startswith("/mnt/"):
		windows_path = posix_path.replace("/mnt/", "")
		windows_path = windows_path[0] + ":/" + windows_path[1:]
	else:
		windows_path = posix_path
	return windows_path

def not_empty_path(path):
	return path is not None and path != "None"

def main():
	mpc_path = "/mnt/c/Program Files/MPC-HC/mpc-hc64.exe"
	video_file = None
	audio_file = None
	susbtitles_file = None
	args = sys.argv[1:]
	while len(args) > 0:
		arg = args.pop(0)
		if arg == "-v":
			video_file = args.pop(0)
		elif arg == "-a":
			audio_file = args.pop(0)
		elif arg == "-s":
			susbtitles_file = args.pop(0)
	command = []
	command.append(mpc_path)
	command.append(posix_path_to_windows_path(video_file))
	if not_empty_path(audio_file):
		command.append("/dub")
		command.append(posix_path_to_windows_path(audio_file))
	if not_empty_path(susbtitles_file):
		command.append("/sub")
		command.append(posix_path_to_windows_path(susbtitles_file))
	print(command)
	subprocess.run(command)

if __name__ == "__main__":
	main()