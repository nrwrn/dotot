from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Dict, List
import yaml

import click


VALID_CONF_NAMES = ['lmy.yml', 'lmay.yaml', 'dotod.yml', 'dotod.yaml']


@click.command('dotod')
@click.argument(
        'paths', nargs=-1, type=click.Path(exists=True, file_okay=False))
def cli_dotod(paths):
    for path in paths:
        dotod(pathify(path))  # TODO: extra path checks?


@click.command('todot')
@click.argument(
        'paths', nargs=-1, type=click.Path(exists=True, file_okay=False))
def cli_todot(paths):
    for path in paths:
        todot(pathify(path))  # TODO: extra path checks?


def dotod(path: Path):
    new_links = 0
    deleted_files = 0
    dead_links = 0
    conf = read_conf(get_conf_path(path))
    for dep in conf.deps:
        dotod(path / dep)
    for tgt, lnn in conf.links.items():
        # TODO: link name relative wouldn't work like this
        if not lnn.exists():
            if lnn.is_symlink():
                lnn.unlink()
                dead_links += 1
            (Path.cwd() / path).mkdir(mode=0o755, parents=True, exist_ok=True)
            lnn.symlink_to(Path.cwd() / path / tgt)
            new_links += 1
        elif lnn.is_symlink() and lnn.readlink() == Path.cwd() / path / tgt:
            # TODO: resolve links in check?
            pass  # link already exists, do nothing
        elif lnn.is_symlink():
            pass  # TODO: move both into folder, concatenate
        elif lnn.is_file():
            if click.confirm('Overwrite %s?' % str(lnn)):
                lnn.unlink()
                deleted_files += 1
                lnn.symlink_to(Path.cwd() / path / tgt)
                new_links += 1
            else:
                print('Did not write %s' % str(lnn))
        else:
            sys.exit('Unexpected type at %s' % str(lnn))
    echo_module_string(path, new_links, deleted_files, dead_links)


def todot(path: Path):
    conf = read_conf(get_conf_path(path))
    for dep in conf.deps:
        todot(dep)  # TODO: recursive?
    for tgt, lnn in conf.links.items():
        pass  # TODO: implement


def get_conf_path(dir_path: Path) -> Path:
    valid_paths = [dir_path / name for name in VALID_CONF_NAMES]
    existing_paths = [path for path in valid_paths if path.exists()]
    if not existing_paths:
        sys.exit('Couldn\'t find config')  # TODO
    if len(existing_paths) > 1:
        sys.exit('Too many configs')  # TODO
    return existing_paths[0]


@dataclass
class Conf():
    deps: List[Path] = field(default_factory=list)
    links: Dict[Path, Path] = field(default_factory=dict)


def read_conf(path) -> Conf:
    with open(path, 'r') as stream:
        conf_dict = yaml.safe_load(stream)
    # TODO: lots of validation and path transformation
    return Conf(
        [pathify(string) for string in conf_dict.get('deps', [])],
        {pathify(src): pathify(dst) for (src, dst)
            in conf_dict.get('links', {}).items()}
    )


def pathify(string: str) -> Path:
    return Path(string).expanduser()


def echo_module_string(
        mod_path: Path,
        new_links: int,
        deleted_files: int,
        dead_links: int):
    strs = []
    if new_links:
        strs.append(f'made {new_links} new links')
    if deleted_files:
        strs.append(f'deleted {deleted_files} files')
    if dead_links:
        strs.append(f'replaced {dead_links} dead links')
    if strs:
        click.echo(f'[{mod_path}] {", ".join(strs)}')
    else:
        click.echo(f'[{mod_path}] did nothing')
