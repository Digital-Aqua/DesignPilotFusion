# DesignPilot for Fusion

*An open-source AI-powered CAD assistant for AutoDesk Fusion.*


## Why DesignPilot?

*blah AI-is-taking-over-the-world blah*

*blah it-can't-do-everything-but-there's-lots-it-can blah*


## Support Us

*to do: premium option, patreon, direct donation, etc.*

*to do: contributing*


## Getting Started

### Via the Autodesk App Store (Recommended)

*(coming soon)&trade;*

*to do: upgrading to premium*


### Manual Install (Zip File)

1. Download the latest release from the [releases page](https://github.com/Digital-Aqua/DesignPilotFusion/releases).
2. Extract the zip file to a location of your choice.
3. Open Fusion and go to **Utilities** Tab &rarr; **Scripts and Add-Ins** &rarr; **Add-Ins** Tab &rarr; **My Add-Ins** &rarr; **+**
4. Select the folder where you extracted the zip file.
5. Repeat this process to update when new versions are released.


### Manual Install (Git Repo)

1. Open a terminal in the folder where you want to clone the repository.
2. Run:
```bash
git clone \
    --branch release \
    --depth 1 \
    --recurse-submodules  \
    https://github.com/Digital-Aqua/DesignPilotFusion.git
```
3. Open Fusion and go to *Utilities* &rarr; *Add-Ins* &rarr; *Add-Ins* Tab &rarr; *My Add-Ins* &rarr; **+**.
4. Select the folder where you cloned the repository.

To update to the latest release version, run:
```bash
git pull
```


### Latest Development Version (Git Repo)

Follow the manual install instructions above, but use the `main` branch instead of the `release` branch:
```bash
git clone \
    --branch main \
    --depth 1 \
    --recurse-submodules \
    https://github.com/Digital-Aqua/DesignPilotFusion.git
```

To update to the latest development version, run:
```bash
git pull
```
