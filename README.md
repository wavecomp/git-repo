WARNING: Under construction.  Not all of the bold strokes claimed here have actually been implemented.  Having said that, we are very keen to get this implemented, so stay tuned.

Repo is a repository management tool that Google built on top of Git. This same project goes by two names: git-repo and tools_repo.

As part of the [Android development environment](https://source.android.com/source/developing), Repo unifies the many Git repositories when necessary, does the uploads to the [revision control system](https://android-review.googlesource.com/), and automates parts of the Android development workflow. Repo is not meant to replace Git, only to make it easier to work with Git in the context of Android. The repo command is an executable Python script that you can put anywhere in your path. In working with the Android source files, you will use Repo for across-network operations. For example, with a single repo command you can download files from multiple repositories into your local working directory.

This fork was enhanced to add:
1. A `repo push` command that performs an ordinary push of the topic branch on all repositories.  This allows you to push the topic branches to GitHub or GitLab, where you can create a pull request or merge request and get your code reviewed.  The existing `repo upload` command continues to upload to Gerrit as usual.
2. All operations are executed in the same order as defined in the manifest file.  In particular, `repo push` and `repo upload` push to the repositories in the same order that the ``<project>`` elements appear in the manifest file.

# Installing and using repo

## Prerequisites
repo requires Python 2.7 or above.  For Python 2.6 (untested), install the `ordereddict` package.

## Installation
To install repo, follow the [repo installation instructions](https://source.android.com/source/downloading).  Of course substiture this GitHub repository for the Google repository as required. 

## Usage
The [Android Developing page](https://source.android.com/source/developing) shows you how to use repo.  The [manifest file reference](docs/manifest-format.txt) explains the contents of the manifest file that you use to describe your repositories.

There is also a handy [repo Command Reference](https://source.android.com/source/using-repo).

# Developer information

The rest of this page is only of interest to developers, not users.

# Repository history

repo has a long history that makes it difficult to discover the canonical repository.

This repository is a fork of Google's https://gerrit.googlesource.com/git-repo/.  It appears that the same code is also served as https://android.googlesource.com/tools/repo/.  These two repository names have given rise to duplicate project names "git-repo" and "tools_repo" ("tools/repo" with '/' replaced with '_').

Due to the [shutdown of Google Code](http://google-opensource.blogspot.com/2015/03/farewell-to-google-code.html0), the original Google Code repo project https://code.google.com/p/git-repo/ is now archived and out of date.

## Resyncing with official google repo

This procedure comes to us from the [esrlabs/git-repo project](https://github.com/esrlabs/git-repo).

For resyncing with the official google repo git, here are the commands for resyncing with the tag v1.12.33 of the official google repo:

    # add google git-repo remote with tag
    git remote add googlesource https://android.googlesource.com/tools/repo/  # Check URL!
    git checkout v1.12.33 -b google-latest

    # checkout basis for resync
    git checkout google-git-repo-base -b update
    git merge --allow-unrelated-histories -Xtheirs --squash google-latest
    git commit -m "Update: google git-repo v1.12.33"
    git rebase stable

    # solve conflicts; keep portability in mind

    git checkout stable
    git rebase update

    # cleanup
    git branch -D update
    git branch -D google-latest


## Creating a new signed version

Commands for creating a new version of repo:

    git tag -s -u KEYID v0.4.16 -m "COMMENT"
    git push origin stable:stable
    git push origin v0.4.16

* replace `KEYID` (something like 0x..)
* the `v0.4.16` (two times)
* replace `COMMENT` with something more explaining

