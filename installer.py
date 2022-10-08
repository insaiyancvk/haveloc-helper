import subprocess, sys, os

import warnings
warnings.filterwarnings("ignore")

subprocess.call(['pip','install','-q','rich'])

dem_packages = [
    'requests',
    'bs4'
    ]

scripts = [
    'https://raw.githubusercontent.com/insaiyancvk/haveloc-helper/main/haveloc.py',
    'https://raw.githubusercontent.com/insaiyancvk/haveloc-helper/main/credentials.json'
]

script_name = [
    'haveloc.py',
    'credentials.json'
]

if os.name == 'nt':
    dem_packages.append('windows-curses')
    os.system('cls')

ROOT_DIR = 'haveloc-helper'

from time import sleep
from rich.console import Console

console = Console()
console.print()

tasks = [n for n in range(len(dem_packages))]
# tasks = dem_packages

with console.status("[bold green]Installing dependencies...") as status:
    while tasks:
        task = tasks.pop(0)
        
        subprocess.call([sys.executable,'-m','pip','--disable-pip-version-check','install','-q',dem_packages[task]])
        
        sleep(1)
        console.log(f"{dem_packages[task]} installation complete")


import requests, pathlib
from rich import print
from rich.filesize import decimal
from rich.markup import escape
from rich.text import Text
from rich.tree import Tree

tasks = [n for n in range(len(scripts))]

try:
    os.mkdir(ROOT_DIR)
except FileExistsError:
    pass

with console.status("[bold green]Installing the scripts...") as status:
    while tasks:
        
        task = tasks.pop(0)
        
        code = requests.get(scripts[task]).text
        
        with open(ROOT_DIR+'/'+script_name[task],'w', encoding="utf-8") as f:
            f.write(code)
        
        sleep(1)
        console.log(f"Saving {script_name[task]}")



def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    # Sort dirs first then by filename
    paths = sorted(
        pathlib.Path(directory).iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )
    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue
        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""
            branch = tree.add(
                f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "green")
            text_filename.highlight_regex(r"\..*$", "bold red")
            text_filename.stylize(f"link file://{path}")
            file_size = path.stat().st_size
            text_filename.append(f" ({decimal(file_size)})", "blue")
            icon = "🐍 " if path.suffix == ".py" else "📄 "
            tree.add(Text(icon) + text_filename)

directory = ROOT_DIR
tree = Tree(
    f":open_file_folder: [link file://{directory}]{directory}",
    guide_style="bold bright_blue",
)
print("\nThe following files have been installed\n")
walk_directory(pathlib.Path(directory), tree)
print(tree)

console.log(f"\nRun 'py manager.py' in {ROOT_DIR} directory")
sleep(3)

console.log(f"\nDownload the respective chromedriver\nAnd place the extracted file \neither in env variables or in the code folder\nOpening the link")
sleep(3)
os.startfile('https://chromedriver.chromium.org/downloads#h.p_ID_32')