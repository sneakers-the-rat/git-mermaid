import pytest
from time import sleep

import tempfile
from pathlib import Path

import git

def make_commit(repo:git.Repo):
    path = Path(repo.working_dir)
    n_heyfiles = len(list(path.glob('*.txt')))
    heyfile = path / f'hey_{n_heyfiles}.txt'
    with open(heyfile, 'w') as hfile:
        hfile.write('hey ')
    repo.index.add([str(heyfile)])
    author = git.Actor('hey', "hey@example.com")
    committer = git.Actor('hey', 'hey@example.com')
    repo.index.commit('added feature: hey', author=author, committer=committer)
    # sleep to ensure commit times are in order
    sleep(0.01)

@pytest.fixture(scope='function')
def repo() -> git.Repo:
    """
    Minimal repo with

    - branching
    - merging
    - commits on parallel branches
    - tags

    :return:
    """
    path = tempfile.TemporaryDirectory()
    repo = git.Repo.init(str(path.name))
    make_commit(repo)
    main = repo.create_head('main')

    # make a few initial commits
    make_commit(repo)
    make_commit(repo)
    # add a tag
    repo.create_tag('v1', ref="HEAD")
    # branch
    dev = repo.create_head('dev')
    make_commit(repo)
    make_commit(repo)

    # switch branches with parallel commits
    repo.heads.main.checkout()
    make_commit(repo)
    make_commit(repo)
    repo.heads.dev.checkout()
    make_commit(repo)
    repo.create_tag('v2', ref="HEAD")

    # third branch from main
    repo.heads.main.checkout()
    feature = repo.create_head('feature')
    make_commit(repo)
    make_commit(repo)

    # cherrypick to main
    # repo.heads.main.checkout()
    # repo.git.cherry_pick(repo.heads.feature.commit)
    # repo.git.cherry_pick('continue')
    #
    # make_commit(repo)
    # repo.heads.feature.checkout()
    # make_commit(repo)

    # merge
    repo.heads.dev.checkout()
    merge_base = repo.merge_base(dev, feature)
    repo.index.merge_tree(dev, base=merge_base)
    feature = repo.heads.feature
    repo.index.commit(
        'merged feature into dev',
        parent_commits=(
          repo.heads.feature.commit,
          repo.heads.dev.commit
        )
    )

    repo.heads.main.checkout()
    dev = repo.heads.dev
    merge_base = repo.merge_base(main, dev)
    repo.index.merge_tree(main, base=merge_base)
    repo.index.commit(
        'merged dev into main',
        parent_commits=(
            repo.heads.main.commit,
            repo.heads.dev.commit
        )
    )

    # one more tag for good measure
    repo.create_tag('v3', ref="HEAD")

    yield repo
    path.cleanup()





