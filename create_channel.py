#!/usr/bin/env python3
"""
Channel Creator Script – Automatically generates a new TV channel folder
with all the minimum required structure and default files.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

def create_channel(channel_name, block_name="default", show_name="show1"):
    """
    Create a new channel with the minimum required structure.

    Args:
        channel_name: Name of the channel (e.g., "nickelodeon")
        block_name: Name of the first block (e.g., "primetime")
        show_name: Name of the first show (e.g., "spongebob")
    """
    # Base paths
    base_dir = Path("channels") / channel_name

    if base_dir.exists():
        print(f"Error: Channel '{channel_name}' already exists at {base_dir}")
        return False

    print(f"Creating new channel: {channel_name}")
    print(f"  Block: {block_name}")
    print(f"  Show: {show_name}")

    # 1. Create channel folder
    base_dir.mkdir(parents=True)
    print(f"  ✓ Created {base_dir}")

    # 2. Create ads and bumpers folders (empty)
    ads_path = base_dir / "channel-ads"
    ads_path.mkdir()
    print(f"  ✓ Created {ads_path}")

    bumpers_path = base_dir / "channel-bumpers"
    bumpers_path.mkdir()
    print(f"  ✓ Created {bumpers_path}")

    # 3. Create blocks folder
    blocks_path = base_dir / "blocks"
    blocks_path.mkdir()
    print(f"  ✓ Created {blocks_path}")

    # 4. Create block folder
    block_path = blocks_path / block_name
    block_path.mkdir()
    print(f"  ✓ Created {block_path}")

    # 5. Create block-bumpers and intro folders
    block_bumpers_path = block_path / "block-bumpers"
    block_bumpers_path.mkdir()
    intro_path = block_bumpers_path / "intro"
    intro_path.mkdir()
    print(f"  ✓ Created {block_bumpers_path} with intro/ subfolder")

    # 6. Create shows folder and show folder
    shows_path = block_path / "shows"
    shows_path.mkdir()
    show_path = shows_path / show_name
    show_path.mkdir()
    print(f"  ✓ Created {show_path}")

    # 7. Create season 1 folder inside show
    season_path = show_path / "S1"
    season_path.mkdir()
    print(f"  ✓ Created {season_path}")

    # 8. Create default schedule.json
    schedule = [
        {
            "days": [0, 1, 2, 3, 4, 5, 6],  # Every day
            "start": "00:00",
            "end": "23:59"
        }
    ]
    schedule_file = block_path / "schedule.json"
    with open(schedule_file, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2)
    print(f"  ✓ Created {schedule_file}")

    # 9. Create default order.json
    order = [
        "ad",
        "channel-bumper",
        "block-bumper",
        show_name,
        "intro",
        "block-bumper",
        "channel-bumper"
    ]
    order_file = block_path / "order.json"
    with open(order_file, 'w', encoding='utf-8') as f:
        json.dump(order, f, indent=2)
    print(f"  ✓ Created {order_file}")

    # 10. Create a README file with instructions
    readme_content = f"""
# {channel_name} Channel

## Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Folder Structure
- `channel-ads/` - Place your channel ads here (.mp4, .mkv, etc.)
- `channel-bumpers/` - Place your channel bumpers here
- `blocks/{block_name}/`
  - `block-bumpers/` - Block-specific bumpers
  - `block-bumpers/intro/` - Intro bumpers (for "intro" in order.json)
  - `shows/{show_name}/`
    - `S1/` - Season 1 episodes (name files like "S1E1 - Title.mp4")
    - `history.json` - Auto-generated watch history
  - `schedule.json` - When this block is on air
  - `order.json` - What to play and in what order

### How to Use
1. Add video files to the appropriate folders
2. Edit `schedule.json` to set your broadcast times
3. Edit `order.json` to customize what plays (use "ad", "channel-bumper", "block-bumper", "intro", or show names)
4. Run `python tv_launcher.py` and double-click your channel

### order.json Values
- `"ad"` - Plays random video from `channel-ads/`
- `"channel-bumper"` - Plays random video from `channel-bumpers/`
- `"block-bumper"` - Plays random video from `block-bumpers/`
- `"intro"` - Plays random video from `block-bumpers/intro/`
- `"show_name"` - Plays the next unwatched episode from `shows/show_name/`

### Supported Video Formats
.mp4, .mkv, .avi, .mov, .wmv, .flv, .webm

### Episode Naming
- Season from folder name: S1, S2, Season 1, Season 2
- Episode from filename: E3, E03, 03, or any number
"""
    readme_file = base_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content.strip())
    print(f"  ✓ Created {readme_file}")

    # 11. Create sample placeholder files (optional)
    # Create a sample .txt file to indicate where to place videos
    placeholder_file = ads_path / "PLACE_VIDEOS_HERE.txt"
    with open(placeholder_file, 'w') as f:
        f.write("Place your ad videos here (.mp4, .mkv, .avi, .mov, .wmv, .flv, .webm)")

    placeholder_file = bumpers_path / "PLACE_VIDEOS_HERE.txt"
    with open(placeholder_file, 'w') as f:
        f.write("Place your channel bumpers here")

    placeholder_file = block_bumpers_path / "PLACE_VIDEOS_HERE.txt"
    with open(placeholder_file, 'w') as f:
        f.write("Place your block bumpers here")

    placeholder_file = intro_path / "PLACE_VIDEOS_HERE.txt"
    with open(placeholder_file, 'w') as f:
        f.write("Place your intro bumpers here")

    placeholder_file = season_path / f"PLACE_{show_name.upper()}_EPISODES_HERE.txt"
    with open(placeholder_file, 'w') as f:
        f.write(f"Place {show_name} season 1 episodes here\n")
        f.write("Name them like: S1E1 - Episode Title.mp4\n")
        f.write("The script will detect: S1E1, S1E2, etc.")

    print(f"  ✓ Created placeholder files")

    print(f"\n✅ Channel '{channel_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  1. Add video files to the folders")
    print(f"  2. Edit {schedule_file} for broadcast times")
    print(f"  3. Edit {order_file} for what to play")
    print(f"  4. Run the GUI: python tv_launcher.py")

    return True


def main():
    # Get channel name from command line or prompt
    if len(sys.argv) >= 2:
        channel_name = sys.argv[1]
    else:
        channel_name = input("Enter channel name (e.g., 'nickelodeon'): ").strip()
        if not channel_name:
            print("Error: Channel name is required.")
            sys.exit(1)

    # Get block name (optional)
    if len(sys.argv) >= 3:
        block_name = sys.argv[2]
    else:
        block_name = input("Enter block name (default: 'default'): ").strip()
        if not block_name:
            block_name = "default"

    # Get show name (optional)
    if len(sys.argv) >= 4:
        show_name = sys.argv[3]
    else:
        show_name = input("Enter first show name (default: 'show1'): ").strip()
        if not show_name:
            show_name = "show1"

    create_channel(channel_name, block_name, show_name)


if __name__ == "__main__":
    main()
