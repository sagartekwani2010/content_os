# Workstation migration handoff for Claude Code

Prepared 15 November 2026 for Sagar's move from this work Mac to a personal
home Mac. **Read this file before declaring the migration complete.** It is a
locator and execution brief. The private cloud archive is uploaded and
verified; restoring it on the home Mac is the remaining migration step.

## What is already on GitHub

- Personal account: `sagartekwani2010`.
- Public source and editorial memory: `https://github.com/sagartekwani2010/content_os`.
  `main` and `claude/reel-system-revamp` were pushed together after the
  migration handoff was updated. The latest branch adds the production-system
  blueprint, Edits helpers, recording kit, new-laptop guide, final learning-
  mission edit diagnosis, and `CLAUDE.md`. The prior `56fb19d` commit added the
  Gym Jarvis/mission context, captions, take maps, and review feedback.
- Source entry points: `AGENTS.md`, `CLAUDE.md`, `CURRENT_REEL_CONTEXT.md`,
  `HANDOFF.md`, `config/brand.yaml`, `feedback/VIDEO_LEARNING_LOOP.md`,
  `feedback/learning-mission-final-edit-diagnosis-2026-11-15.md`, and
  `planning/reel-production-system-blueprint-2026-11-15.md`.
- The public repository does **not** contain all footage, transcripts, rendered
  MP4s, Edits projects, downloaded music, or ignored personal files.
- The **private personal** media repository is
  `https://github.com/sagartekwani2010/content-os-media`. Its published
  [migration release](https://github.com/sagartekwani2010/content-os-media/releases/tag/migration-2026-11-15)
  has eight archive parts and `manifest.json`. Keep the repo private.
- `invideo_recreate` / TakeSelect Lab is a separate tool checkout at
  `/Users/sagart/Desktop/Consolidated_Codebase/invideo_recreate`, clean at
  `8588ee4`, with remotes under `hs-tekwani-sagar` (`takeselect-lab` and
  `takeselect-editor`). That is a professional account. Do not move personal
  footage into either professional Git repository. Its ignored `runtime/`
  directory **does** hold personal editing artifacts and must be backed up to
  the personal media archive.

## Project status that must survive the move

- **Gym Jarvis launch:** main and trial exports are local. The 51.07-second
  picture uses selected `IMG_3470.MOV` voice at 1.2× with pitch preserved. Main
  score: Mixkit Techno Fest Vibes; trial: Memory Reboot in Edits. The bad Why
  frame around 19 seconds and blank opening frames were repaired. Main later
  had some traction relative to earlier Reels; trial performed poorly. No
  measured retention/reach figures were supplied. See
  `outputs/gym-jarvis-launch/` and `feedback/gym-jarvis-and-learning-mission-2026-11-15.md`.
- **Agentic AI learning-mission Reel:** the creator posted an Edits export of
  the v7 project (roughly 63 seconds, 1.25×), then judged it poor: abrupt face
  cuts, interview-extract feel, unclear job, quiet voice, and no music in the
  export. The prior v3 selects are not the final post. Read
  `feedback/learning-mission-final-edit-diagnosis-2026-11-15.md`; do not repeat
  that workflow. A newer local v8 render exists in TakeSelect `runtime/` and
  must be preserved as an artifact, not mistaken for the posted version.
- **Next work:** build the staged production pipeline before the next Reel.
  Food tracker is the teased topic. The 60-second cap is dropped. The creator
  wants line-by-line or voiceover-led recording, one clear job per Reel, and one
  finished export with mastered voice, SFX, and music. The creator must listen
  to that exact final file. See `production/RECORDING_KIT.md` and
  `planning/reel-production-system-blueprint-2026-11-15.md`.

## Local files included in the private personal archive

Use `$OLD_HOME=/Users/sagart` on the old Mac. These directories are not
covered by the public Git push. Sizes are approximate, measured 15 November
2026. The archive contains 2,338 files, totaling 13,279,774,619 source bytes.

| Source on old Mac | Approx. size | Contents / why it matters |
| --- | ---: | --- |
| `$OLD_HOME/Downloads/IMG_3470.MOV` | 1.14 GiB | Original Gym Jarvis voice/video takes. |
| `$OLD_HOME/Downloads/IMG_3479.MOV` | 2.83 GiB | Original 47-minute mission recording; essential for re-edits. GitHub requires this file to be split for a release upload. |
| `$OLD_HOME/Movies/GymJarvis/` | 1.92 GiB | Gym Jarvis edit versions, voice WAVs, audio, music and SFX source, EDLs, scripts, notes, captures. Preserve the full directory. |
| `$OLD_HOME/Documents/Codex/2026-11-12/for/outputs/` | 0.33 GiB | Main/trial final MP4s and covers, captions, edit notes, mission v1-v3 selects. |
| `$OLD_HOME/Documents/Codex/2026-11-12/for/work/` | 1.19 GiB | Source/full transcripts (`agentic_mission/transcript_full.json`, `transcript.json`, `transcript.vtt`), take manifests, clip/QC evidence, intermediate renders, graphics, downloaded Whisper model. Preserve scripts and text as well as media. |
| `$OLD_HOME/Desktop/Consolidated_Codebase/invideo_recreate/runtime/` | 4.3 GiB | Ignored personal editing runtime: full/revised/polish cut transcripts, EDLs, photo B-roll, v4-v8 mission renders, team pilot outputs. Do not commit it to the professional repo. |
| `$OLD_HOME/Library/Containers/com.burbn.basel.mac/Data/Documents/agentic_mission_v4/` | 3.5 GiB | Edits working assets, screenshots, v4-v7 exports, cover and a duplicate of `IMG_3479.MOV`. Preserve project assets. |
| `$OLD_HOME/Movies/Edits/Exports/` | 0.15 GiB | Includes the posted mission v7 export. |
| `$OLD_HOME/Desktop/content_os/demos/workout-hud/app/media/` | 1.6 MiB | Six ignored personal meal/body photos used by the HUD. |
| `$OLD_HOME/Desktop/content_os/content_os*.db` | ~1 MiB | Three ignored local databases; preserve without placing them in public Git. |
| `$OLD_HOME/Desktop/content_os/sites/sagar-agent-authority/` | small | Ignored local Site checkout; back up relevant source/build files if needed, excluding nested `.git` and credentials. |

The copy of `IMG_3479.MOV` in the Edits Documents folder is **byte-identical**
to the Downloads original (SHA-256
`e6f6372fb31b6de8462d9b8dd943df20fa764dda64c6ee7d4c075509459c7c75`).
One archive copy is enough if the restore instructions recreate the Edits path.
Other duplicate MP4s can be deduplicated only after comparing hashes. Preserve
all distinct versions and manifests. Do not omit a final or posted version just
because an earlier version has a similar name.

The Edits app may keep project metadata outside `Data/Documents`; verify
project portability with the app or its native export before relying on a folder
copy. Do not back up the entire app container blindly: it can include account
state and tokens. The media archive should contain source footage and export
assets; the app/project re-link step may still be required on the home Mac.

## Archive and restore

1. Keep `content_os` public for code, text context, approved learnings, small
   shareable graphics, and scripts. Keep personal footage, message screenshots,
   audio, databases, and licensed tracks in the **private personal** media repo.
2. GitHub rejects ordinary Git files over 100 MiB. The media is in a private
   GitHub release, tag `migration-2026-11-15`, as eight numbered split tar
   parts (each below 2 GiB) plus `manifest.json`. The manifest records
   relative paths, byte sizes, and SHA-256 checksums. No large binary files
   were committed to either source repo or the professional account.
3. Exclude `.env`, tokens, cookies, keychains, app session data, `.git/`,
   `.venv/`, caches and installed third-party package trees. Reinstall tools on
   the new Mac. Preserve creator-authored scripts, notes, transcripts, EDLs and
   distinct rendered media. If the Whisper model is omitted as a redownloadable
   dependency, record that explicitly in the manifest.
4. The archive index and `restore_media.py` are in the private repo. Any
   Git commit made from Codex must include
   `Co-authored-by: Codex <noreply@openai.com>` in the commit body. Keep all
   credentials out of Git history and release assets.
5. The repo was confirmed private. All nine release assets were checked
   against local size and SHA-256; GitHub reports matching digests. The release
   manifest and part 008 were downloaded again and matched SHA-256. A complete
   local extraction of all eight parts verified all 2,338 extracted files.
6. On the home Mac, authenticate `gh` to the **personal** GitHub account and
   run:

   ```bash
   gh repo clone sagartekwani2010/content-os-media
   mkdir -p ~/content-os-media-release ~/content-os-media-staging
   gh release download migration-2026-11-15 --repo sagartekwani2010/content-os-media --dir ~/content-os-media-release
   python3 content-os-media/restore_media.py ~/content-os-media-release ~/content-os-media-staging
   ```

   `restore_media.py` checks each part and each extracted file. Copy the
   verified staging files to the corresponding paths listed above, then
   reinstall dependencies, re-link Edits media, and run
   `.venv/bin/python -m pytest tests -q` (180 tests passed on the old Mac).
   `production/SETUP_NEW_LAPTOP.md` covers the rest of the tool setup.

## Exact status at handoff

- Public `content_os/main`: pushed with this handoff; tests: **180 passed**;
  new Edits helper modules compiled.
- Private `content-os-media`: **published and verified private** at release
  `migration-2026-11-15`, with eight parts and a manifest. A sample was
  downloaded and verified, and the full archive passed a local restore test.
- TakeSelect source checkout: clean; personal `runtime/` is in the private
  archive and remains ignored by the professional repo.
- Source footage, transcripts, covers, music, Edits assets and rendered videos
  listed above are in the private release. Home Mac download and restore are
  still pending.
- No credential file was copied. The old machine must not be wiped until the
  private release has been downloaded and verified on the home Mac.

## Prompt to give Claude Code

> Read `AGENTS.md`, `CLAUDE.md`, and `WORKSTATION_MIGRATION_HANDOFF.md` in
> `content_os`. The private media backup is already in the published
> `migration-2026-11-15` release of `sagartekwani2010/content-os-media`.
> On the home Mac, download all nine assets while authenticated to the personal
> GitHub account. Run `restore_media.py`, which verifies the archive and all
> extracted files, then place the staged files into the corresponding home-Mac
> locations. Keep personal media out of the public `content_os` and
> professional TakeSelect repositories. Re-link Edits projects, run the source
> tests, and verify a playable final export before the old Mac is wiped.
