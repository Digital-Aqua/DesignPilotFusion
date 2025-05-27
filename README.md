# DesignPilot for Fusion

*An open-source AI-powered CAD assistant for AutoDesk Fusion.*


## Why DesignPilot?

*blah AI-is-taking-over-the-world blah*

*blah it-can't-do-everything-but-there's-lots-it-can blah*


## Support Us

*to do: premium option, patreon, direct donation, etc.*

*to do: contributing*


## Installation

### Via the Autodesk App Store (Recommended)

*(coming soon)&trade;*

*to do: upgrading to premium*


### Manual Install (Zip File)

1. Download the latest release from the [releases page](https://github.com/Digital-Aqua/DesignPilotFusion/releases).

2. Extract the zip file to a location of your choice.

3. Open Fusion and go to **Utilities** Tab &rarr; **Scripts and Add-Ins** &rarr; **Add-Ins** Tab &rarr; **My Add-Ins** &rarr; **+**

4. Select the folder where you extracted the zip file.

5. Repeat this process to update when new versions are released.


### Manual Clone &amp; Build

1. Clone the repository.

2. Install [conda](https://conda-forge.org/download/)

3. Create a conda development environment.

4. Install [task](https://taskfile.dev/installation/)

5. Run the following commands:

```bash
git clone \
    --branch release \
    --depth 1 \
    --recurse-submodules  \
    https://github.com/Digital-Aqua/DesignPilotFusion.git
cd DesignPilotFusion
conda create --yes --prefix ./.conda
conda activate ./.conda
conda install --yes go-task
task dev-setup
```

6. Build the add-in to the repo's `.build` subfolder with the command:

```bash
task build-all
```

7. Open Fusion and go to **Utilities** &rarr; **Scripts and Add-Ins** &rarr; **Add-Ins** Tab &rarr; **My Add-Ins** &rarr; **+**.

8. Select the folder `<repo>/.build/DesignPilotFusion`.

9. Update to the latest version with the commands:

```bash
git pull
task build-all
```

### Development Clone &amp; Build

Follow **Manual Clone &amp; Build** instructions above, replacing `--branch release` with `--branch main` to get the latest development version.

