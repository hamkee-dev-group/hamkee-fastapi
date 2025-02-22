# Quickstart

## Clone repo

The first step is to clone the repository.

```bash
git clone https://github.com/edvm/result-api.git
```

After you clone the repo, execute **cd result-api**, you should see the followign directory structure:

```bash
➜  cd result-api 
➜  result-api git:(main) ls -l
total 24
drwxr-xr-x  11 edvm  staff   352B Mar  2 14:54 .
drwxr-xr-x@  6 edvm  staff   192B Mar  2 14:54 ..
drwxr-xr-x  12 edvm  staff   384B Mar  2 14:54 .git
drwxr-xr-x   3 edvm  staff    96B Mar  2 14:54 .github
-rw-r--r--   1 edvm  staff   3.2K Mar  2 14:54 .gitignore
-rw-r--r--   1 edvm  staff   1.9K Mar  2 14:54 README.md
drwxr-xr-x   8 edvm  staff   256B Mar  2 14:54 app
drwxr-xr-x   4 edvm  staff   128B Mar  2 14:54 docs
-rw-r--r--   1 edvm  staff   593B Mar  2 14:54 result.example
drwxr-xr-x   4 edvm  staff   128B Mar  2 14:54 scripts
drwxr-xr-x   4 edvm  staff   128B Mar  2 14:54 tests
```

## Create .result file

Next, you need to create a .**result** file (at result-api root directory), where *environment variables* are defined to generate configuration files. It also works as an *.env* file, where its values are available both in the current environment and if the project is run within a docker container. The project provides a *result.example* file, copy and paste this file and edit it with the corresponding values for your project.

So execute **cp result.example .result**:

```bash
➜  result-api git:(main) cp result.example .result
```

## Run the installer

Now run the installer. The installer, using the values you set on **.result** file, will auto-generate files for docker, docker compose, pyproject, requirements, etc. It'll download the Python version you specified, it'll create a virtual environment, install the project requirements on it, etc.

Run the installer by executing **./scripts/devel/localenv.sh install**

```bash
result-api git:(main) ./scripts/devel/localenv.sh install
```

### Rye installer

If it is the first time you run it, it'll install [Rye](https://rye-up.com/) (Python interpreter and virtual environment manager). It is suggested to respond with the following values to the questions made by the installer:

1- When asked to continue, say **y**:

```bash
This script will automatically download and install rye (latest) for you.
######################################################################## 100.0%
Welcome to Rye!

This installer will install rye to /Users/edvm/.rye
This path can be changed by exporting the RYE_HOME environment variable.

Details:
  Rye Version: 0.27.0
  Platform: macos (aarch64)

? Continue? (y/n) ›
```

2- When asked to choose between **pip-tools** or **uv**, select **uv** :

```bash
? Select the preferred package installer ›
  pip-tools (slow but stable)
❯ uv (quick but experimental)
```

3- When asked what should happen when typing **python** outside a **Rye** project select: *Run the old default Python (provided by your OS, pyenv, etc.)* :

```bash
? What should running `python` or `python3` do when you are not inside a Rye managed project? ›
  Run a Python installed and managed by Rye
❯ Run the old default Python (provided by your OS, pyenv, etc.)
```

4- When asked to add **rye** to your $PATH, say **y**:

```bash
The rye directory /Users/edvm/.rye/shims was not detected on PATH.
It is highly recommended that you add it.
? Should the installer add Rye to PATH via .profile? (y/n) ›
```

That's it!

## Post install

You're ready to run the project on your local machine or inside a docker container. It's up to you how do you want to proceed.

Code will be **auto-reloaded** after any change you make on the source code (**hot-reloading**), both if running the project on your local or within Docker.

### Running on my local

First thing to do is open a new terminal OR run  **source ~/.rye/env**.

Second thing is to run the API. Do it by executing **./scripts/devel/localenv.sh up**.

```bash
➜  result-api git:(main) ✗ ./scripts/devel/localenv.sh up
2024-03-02 15:20:15.568 | INFO     | main:<module>:31 - CORS allowed for all origins.
2024-03-02 15:20:15.844 | INFO     | main:<module>:31 - CORS allowed for all origins.
[2024-03-02 15:20:15 -0500] [70608] [INFO] Running on http://0.0.0.0:7000 (CTRL + C to quit)
INFO:hypercorn.error:Running on http://0.0.0.0:7000 (CTRL + C to quit)
```

Open your web browser and point it to **http://localhost:7000/api/v1/hello** , you should get back a JSON response like:

```json
{"message":"Hello World"}
```

### Running with Docker

The installer already auto-generated a dockerfile and docker compose files so just run **docker compose up**

```bash
➜  result-api git:(main) ✗ docker compose up     
... blah, blah, blah ...
 ✔ Container orion  Recreated                                                                                                    0.1s 
Attaching to orion
orion  | 2024-03-02 20:31:27.220 | INFO     | main:<module>:31 - CORS allowed for all origins.
orion  | 2024-03-02 20:31:27.528 | INFO     | main:<module>:31 - CORS allowed for all origins.
orion  | [2024-03-02 20:31:27 +0000] [8] [INFO] Running on http://0.0.0.0:7000 (CTRL + C to quit)
orion  | INFO:hypercorn.error:Running on http://0.0.0.0:7000 (CTRL + C to quit)
```
