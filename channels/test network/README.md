# test network Channel

## Created: 2026-08-26 22:53:06

### Folder Structure
- `channel-ads/` - Place your channel ads here (.mp4, .mkv, etc.)
- `channel-bumpers/` - Place your channel bumpers here
- `blocks/default/`
  - `block-bumpers/` - Block-specific bumpers
  - `block-bumpers/intro/` - Intro bumpers (for "intro" in order.json)
  - `shows/sponge rob/`
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