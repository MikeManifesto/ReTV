#!/usr/bin/env python3
"""
TV Channel Emulator – Bulletproof.
Supports show-intro-bump: plays intro bump of the next show.
"""

import json
import random
import re
import subprocess
import time
import sys
import os
import socket
import signal
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
MPV_SOCKET = "/tmp/mpv-tv-ipc.sock"

# List of special order items (non-shows)
SPECIAL_ITEMS = {"ad", "channel-bumper", "block-bumper", "intro", "show-intro-bump"}

# Handle SIGTERM gracefully
def signal_handler(sig, frame):
    mpv_quit()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_video_files(folder):
    if not folder.is_dir():
        return []
    files = []
    for ext in VIDEO_EXTENSIONS:
        files.extend(folder.rglob(f'*{ext}'))
        files.extend(folder.rglob(f'*{ext.upper()}'))
    return files

def pick_random_video(folder):
    files = get_video_files(folder)
    if not files:
        raise FileNotFoundError(f"No video files found in {folder}")
    return random.choice(files)

def parse_season_from_folder(folder_path):
    folder_name = folder_path.name
    m = re.search(r'S(\d+)', folder_name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r'Season\s*(\d+)', folder_name, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None

def parse_episode_from_filename(filename):
    # First try: look for x pattern (e.g., "4x20")
    m = re.search(r'(\d+)x(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(2))
    # Second: E pattern
    m = re.search(r'E(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Third: standalone numbers - take the LAST one
    numbers = re.findall(r'\b(\d{1,3})\b', filename)
    valid_numbers = [int(n) for n in numbers if int(n) < 1000]
    if valid_numbers:
        return valid_numbers[-1]
    return None

def parse_episode_old(filename):
    m = re.search(r'S(\d+)E(\d+)', filename, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

def get_available_episodes(show_path):
    episodes = []
    for video in get_video_files(show_path):
        parent = video.parent
        season = parse_season_from_folder(parent)
        if season is None:
            s, e = parse_episode_old(video.name)
            if s is not None:
                season, episode = s, e
            else:
                season = 1
                episode = parse_episode_from_filename(video.name)
                if episode is None:
                    episode = 0
        else:
            episode = parse_episode_from_filename(video.name)
            if episode is None:
                episode = 0
        episodes.append((season, episode, video))
    episodes.sort(key=lambda x: (x[0], x[1] if x[1] != 0 else float('inf')))
    season_groups = {}
    for s, e, vid in episodes:
        if e == 0:
            season_groups.setdefault(s, []).append(vid)
    for s, vid_list in season_groups.items():
        for idx, vid in enumerate(vid_list, start=1):
            for i, (s2, e2, vid2) in enumerate(episodes):
                if vid2 == vid and e2 == 0:
                    episodes[i] = (s, idx, vid)
                    break
    episodes.sort(key=lambda x: (x[0], x[1]))
    return episodes

def get_history(show_path):
    history_file = show_path / 'history.json'
    if not history_file.exists():
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return set()
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
            else:
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                return set()
    except (json.JSONDecodeError, ValueError, OSError):
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return set()

def update_history(show_path, episode_id):
    history = get_history(show_path)
    history.add(episode_id)
    history_file = show_path / 'history.json'
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(sorted(history), f, indent=2)

def pick_next_episode(show_path):
    episodes = get_available_episodes(show_path)
    if not episodes:
        raise FileNotFoundError(f"No episodes found in {show_path}")
    history = get_history(show_path)
    for s, e, video in episodes:
        ep_id = f"S{s}E{e}"
        if ep_id not in history:
            return video, ep_id
    history_file = show_path / 'history.json'
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump([], f)
    s, e, video = episodes[0]
    return video, f"S{s}E{e}"

def is_scheduled(schedule, now):
    weekday = now.weekday()
    current_time = now.time()
    for slot in schedule:
        if weekday in slot['days']:
            start = datetime.strptime(slot['start'], '%H:%M').time()
            end = datetime.strptime(slot['end'], '%H:%M').time()
            if start <= current_time <= end:
                return True
    return False

def find_active_block(blocks_path, now):
    if not blocks_path.is_dir():
        return None
    for block_dir in blocks_path.iterdir():
        if not block_dir.is_dir():
            continue
        schedule_file = block_dir / 'schedule.json'
        if not schedule_file.exists():
            continue
        try:
            schedule = load_json(schedule_file)
            if is_scheduled(schedule, now):
                return block_dir
        except Exception:
            continue
    return None

# ------------------------------------------------------------
# mpv IPC control
# ------------------------------------------------------------
def send_mpv_command(command, socket_path=MPV_SOCKET, timeout=2):
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect(socket_path)
        sock.sendall((json.dumps(command) + "\n").encode())
        response = sock.recv(4096).decode()
        sock.close()
        return response
    except Exception:
        return None

def mpv_play_file(video_path):
    cmd = {"command": ["loadfile", str(video_path), "replace"]}
    response = send_mpv_command(cmd)
    if not response or not ('"error":"success"' in response or '"error": "success"' in response):
        return False
    time.sleep(0.3)
    for _ in range(3):
        send_mpv_command({"command": ["set_property", "pause", False]})
        send_mpv_command({"command": ["play"]})
        time.sleep(0.1)
    return True

def mpv_quit():
    send_mpv_command({"command": ["quit"]})

def start_mpv():
    try:
        os.unlink(MPV_SOCKET)
    except FileNotFoundError:
        pass
    with open("/tmp/mpv-input.conf", "w") as f:
        f.write("ESC quit\n")
    proc = subprocess.Popen([
        "mpv",
        "--fullscreen",
        "--keep-open=always",
        "--idle",
        "--input-ipc-server=" + MPV_SOCKET,
        "--input-conf=/tmp/mpv-input.conf",
        "--force-window=immediate",
        "--pause=no",
        "--no-resume-playback",
        "--cache=no",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        if os.path.exists(MPV_SOCKET):
            return proc
        time.sleep(0.1)
    return None

def wait_for_eof():
    while True:
        response = send_mpv_command({"command": ["get_property", "eof-reached"]})
        if response is None:
            return False
        if '"data": true' in response or '"data":true' in response:
            return True
        pause_check = send_mpv_command({"command": ["get_property", "pause"]})
        if pause_check and '"data": true' in pause_check:
            send_mpv_command({"command": ["set_property", "pause", False]})
            send_mpv_command({"command": ["play"]})
        time.sleep(0.5)

# ------------------------------------------------------------
# Order navigation
# ------------------------------------------------------------
def find_next_show(order, current_index):
    """Find the next show name in the order list (cycling)."""
    n = len(order)
    for i in range(1, n + 1):
        idx = (current_index + i) % n
        item = order[idx]
        if item not in SPECIAL_ITEMS:
            return item
    return None

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    channel_name = sys.argv[1]

    base_path = Path("channels") / channel_name
    if not base_path.is_dir():
        sys.exit(1)

    blocks_path = base_path / "blocks"
    if not blocks_path.is_dir():
        sys.exit(1)

    mpv_proc = None

    def ensure_mpv():
        nonlocal mpv_proc
        if mpv_proc is None or mpv_proc.poll() is not None:
            try:
                os.unlink(MPV_SOCKET)
            except:
                pass
            mpv_proc = start_mpv()
            if mpv_proc is None:
                time.sleep(2)
                mpv_proc = start_mpv()
                if mpv_proc is None:
                    sys.exit(1)
        return mpv_proc

    ensure_mpv()

    while True:
        ensure_mpv()
        now = datetime.now()
        active_block = find_active_block(blocks_path, now)
        if active_block is None:
            time.sleep(30)
            continue

        order_file = active_block / 'order.json'
        if not order_file.exists():
            time.sleep(30)
            continue

        order = load_json(order_file)
        ads_path = base_path / "channel-ads"
        channel_bumpers_path = base_path / "channel-bumpers"
        block_bumpers_path = active_block / "block-bumpers"
        intro_path = block_bumpers_path / "intro"

        # Keep track of current order index for show-intro-bump
        order_index = 0

        while True:
            if not is_scheduled(load_json(active_block / 'schedule.json'), datetime.now()):
                break

            ensure_mpv()

            # Loop over order items
            while order_index < len(order):
                if not is_scheduled(load_json(active_block / 'schedule.json'), datetime.now()):
                    break

                item = order[order_index]
                current_idx = order_index
                order_index += 1
                if order_index >= len(order):
                    order_index = 0

                ensure_mpv()

                try:
                    if item == "ad":
                        video = pick_random_video(ads_path)
                    elif item == "channel-bumper":
                        video = pick_random_video(channel_bumpers_path)
                    elif item == "block-bumper":
                        video = pick_random_video(block_bumpers_path)
                    elif item == "intro":
                        video = pick_random_video(intro_path)
                    elif item == "show-intro-bump":
                        # Find the next show in the order
                        next_show = find_next_show(order, current_idx)
                        if next_show is None:
                            # No show found, skip
                            continue
                        show_path = active_block / "shows" / next_show
                        if not show_path.is_dir():
                            continue
                        intro_bump_path = show_path / "show-intro-bump"
                        if not intro_bump_path.exists():
                            continue
                        video = pick_random_video(intro_bump_path)
                    else:
                        # It's a show name
                        show_path = active_block / "shows" / item
                        if not show_path.is_dir():
                            continue
                        video, ep_id = pick_next_episode(show_path)

                    # Play the video
                    if not mpv_play_file(video):
                        continue

                    if not wait_for_eof():
                        mpv_quit()
                        sys.exit(0)

                    # Update history for episodes only
                    if item not in SPECIAL_ITEMS:
                        update_history(show_path, ep_id)

                except FileNotFoundError:
                    time.sleep(0.5)
                    continue
                except KeyboardInterrupt:
                    mpv_quit()
                    sys.exit(0)

                time.sleep(0.2)

            # If we broke out because schedule ended, go to outer loop
            if not is_scheduled(load_json(active_block / 'schedule.json'), datetime.now()):
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        mpv_quit()
        sys.exit(0)
