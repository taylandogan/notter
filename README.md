<div align="center">
    <img src="media/notter.png" alt="logo" width="200"/>
</div>


# notter
<!-- /// Github badges go here -->
![3.10](https://img.shields.io/github/actions/workflow/status/taylandogan/notter/tests.yml?branch=master&event=push&matrix.python-version=3.10&label=python3.10)
![3.11](https://img.shields.io/github/actions/workflow/status/taylandogan/notter/tests.yml?branch=master&event=push&matrix.python-version=3.11&label=python3.11)
![PyPI version](https://img.shields.io/pypi/v/notter?color=blue&label=version&logoColor=red)
[![License: MIT](https://img.shields.io/github/license/taylandogan/notter?color=yellow)](https://opensource.org/licenses/MIT)
![Downloads](https://img.shields.io/pypi/dm/notter?color=red)
![sponsors](https://img.shields.io/github/sponsors/taylandogan?color=teal)


<b>A simple tool with a CLI that enables you to manage your comments and todos in a codebase.</b>

Notter parses your Python codebase, discovers/extracts comments and todos. Also it gives you a CRUD interface for notes/todos. Thus, you can use it as a tool to interact with comments/todos in your codebase without leaving your terminal. Yet, the main idea is to use this project as a backend for an IDE plugin. Such a plugin is already being written for VSCode, which you can find here: https://github.com/taylandogan/notter-vscode

The project still lacks a lot of features. Please see the roadmap below.
<hr>

## Installation
Notter requires Python >= 3.10 and it could be installed via pip.
   ```sh
   $ pip install notter
   ```

If you'd like to contribute to Notter, please check the `Makefile`, it is a good point to start. You can fork & clone this repo and run `make venv_dev` command to install it locally with dev dependencies. Then you can run tests and check if everything is okay by running the following command: `make format test`
<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->
<hr>


## Usage
To be able to use Notter for your project, first you need to initialize it. And it requires you to export your source folder as an env variable called `SRC_PATH`.
```sh
$ export SRC_PATH=/full/path/to/your/source/folder
```
Notter requires this because it creates a `.notter` folder on the same level and location as your source folder. The tool keeps comments/todos along with their metadata under this folder.  Here's an example of the folder structure once you initialize Notter:
```
my_project
├── .notter                    ┐
│   ├── config.json            │  Notter config file
│   │                          │
│   └── notes.db               ┘  Notter database
│
├── src                        ┐
│   └── myPackage              │
│       ├── __init__.py        │ Project source code
│       ├── moduleA.py         │
│       └── moduleB.py         ┘
└── tests                      ┐
   └── ...                     ┘ Package tests
```

### Initialize

To initialize Notter in a codebase, after exporting `SRC_PATH`, run the command below. You also provide a username and email so that Notter can keep track of who created which todo, etc. **Don't worry though! Everything is local, you are not creating an account or signing in anywhere.** Think of it something like a git username/email config. In fact, you might use your git credentials for Notter as well. Note that, while `idx_notes.json` is meant to be tracked by your version control software, `config.json` includes user-specific data, hence it should not be tracked. Please add it to `.gitignore` if you are using git.
```sh
$ notter --init [USERNAME] [EMAIL]
```

### Discover

Once you initialized your Notter instance for the codebase, you can run the discover command to explore the codebase and extract all the comments/todos. This command populates the notes database (notes.db in the folder structure above), creates the content files and prints the found comments/todos in JSON format. Thus, it can create a big diff.

```sh
$ notter discover
```

You might also want to format the output as follows:
```sh
$ notter discover | python -m json.tool
```

### CRUD operations
You can create, read, update and delete comments/todos from the Notter database using the following commands. Note that these commands do not actually touch your source code and only update your Notter instance and its database. (Thus, running these commands without actually doing the changes in the source code would create inconsistencies in your Notter instance. But you can always use the discover command above to reset it.)

```sh
$ notter create [FILEPATH] [LINE] [CONTENT] [TYPE]
$ notter read [FILEPATH] [LINE]
$ notter update [FILEPATH] [LINE] [CONTENT] [TYPE]
$ notter delete [FILEPATH] [LINE]
```

where `[TYPE]` is an accepted value of enum type `NoteType`.

### Version
You can also query the version of your Notter package as follows:
```sh
$ notter --version
```

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->
<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->
<hr>

## Roadmap
Both comments and todos are reffered as "notes".

- [x] Notter instance/index structure
- [x] Detect notes in Python codebases
- [x] CRUD functionality for notes
- [x] Fetch notes of a given file
- [x] Fetch notes including a given keyword
- [ ] Add attributes to notes (priority, reminder, etc.)
- [ ] Auto-prioritization based on attributes
- [ ] Fetch notes with a given attribute
- [ ] Detect notes with tags provided by user
- [ ] Configurable glob patterns to include/exclude files
- [ ] Fetch notes within N lines of a given filepath/line
- [ ] Multi-language support
- [ ] Export notes
- [ ] Archive notes
- [ ] Change username/email

See the [open issues](https://github.com/taylandogan/notter/issues) for a full list of proposed features (and known issues).
<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->
<hr>

## License
See `LICENSE.md` for more information.
<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->
