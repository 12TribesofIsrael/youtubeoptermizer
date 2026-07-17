# Post-Production drop folder

Drop a **ready-to-go** video here, then run:

```bash
python scripts/post_produce.py
```

The script auto-picks the newest video in this folder, wraps it with the
branded intro + outro (`assets/postproduction/intro_outro.mp4`) and a logo
watermark (`assets/postproduction/logo1.png`), and writes the finished file to
`output/<name>_final.mp4`.

Video files here are gitignored (`*.mp4` etc.) — this folder is a local
scratch space, not committed content.

See `scripts/post_produce.py` for flags (`--split`, `--width`, `--no-logo`).
