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


### Manual Build & Install (Git Repo)

1. Check you have [git](https://git-scm.com/downloads) and [conda-forge](https://conda-forge.org/download/) installed.

2. Open a terminal in the folder where you want to clone the repository.

3. Run:
```bash
git clone \
    --branch release \
    --depth 1 \
    --recurse-submodules  \
    https://github.com/Digital-Aqua/DesignPilotFusion.git
```
*If you like to live dangerously, change the branch to `main` to get the latest development version.*

4. Set up your development environment with the command:
```bash
./build.sh --dev-setup
```
This will detect your Fusion installation and copy autocompletion files for your IDE.

5. Build the add-in to the repo's `.build` subfolder with the command:
```bash
./build.sh
```

6. Open Fusion and go to **Utilities** &rarr; **Scripts and Add-Ins** &rarr; **Add-Ins** Tab &rarr; **My Add-Ins** &rarr; **+**.

7. Select the folder `<repo>/.build/DesignPilotFusion`.

To update to the latest version, run:
```bash
git pull
./build.sh --clean
```
