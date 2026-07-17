# Post-Production assets

Required by `scripts/post_produce.py`:

| File | Purpose |
|------|---------|
| `intro_outro.mp4` | Merged brand clip. The script splits it at `--split` seconds (default 26): everything before the split plays as the **intro**, everything after plays as the **outro**. |
| `logo1.png` | Transparent-background PNG logo, overlaid bottom-left on the **main video only** (the brand clip is already branded). |

Both binaries are gitignored (`*.mp4`, `*.png`) — this repo is public, so the
assets live locally only. They were copied from
`ai-bible-gospels/workflows/biblical-cinematic/assets/` (the source pipeline).
To refresh them, re-copy from there.
