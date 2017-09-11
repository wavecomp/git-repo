STATUS: This seems to be functionally complete--alpha quality.

Repo is a repository management tool that Google built on top of Git. This fork provides a new `repo push` command. 

As part of the [Android development environment](https://source.android.com/source/developing), Repo unifies the many Git
repositories when necessary, does the uploads to the [revision control system](https://android-review.googlesource.com/),
and automates parts of the Android development workflow. Repo does not replace Git, it just makes it easier to work with
Git in the context of multiple repositories. The repo command is an executable Python script that you can put anywhere
in your path. In working with the Android source files, you will use Repo for across-network operations. For example,
with a single repo command you can pull files from multiple repositories into your local working copy.

This fork was enhanced to add:
1. A `repo push` command that performs an ordinary push of the topic branch on all repositories.  This allows you to
   push the topic branches to GitHub or GitLab, where you can create a pull request or merge request and get your code
   reviewed.  The existing `repo upload` command continues to upload to Gerrit as usual.
2. All operations are executed in the same order as defined in the manifest file.  In particular, `repo push` and
   `repo upload` push to the repositories in the same order that the ``<project>`` elements appear in the manifest file.

# Installing and using repo

## Prerequisites
repo requires Python 2.7 or above.  For Python 2.6 (untested), you must install the `ordereddict` package before using
repo.

## Installation
To install repo, follow the [repo installation instructions](https://source.android.com/source/downloading).  Of course
substiture this GitHub repository for the Google repository as required.

## Usage
The [Android Developing page](https://source.android.com/source/developing) shows you how to use repo.  If you want do
an ordinary push, use `repo push` command in place of `repo upload`.  If you wish to upload to Gerrit, use `repo upload`
as instructed.

The [manifest file reference](docs/manifest-format.txt) explains the contents of the manifest file that you use to
describe your repositories.

There is also a handy [repo Command Reference](https://source.android.com/source/using-repo).  This does not include
`repo push` documentation, but this command will print it:

    repo help push

# Developer information

The rest of this page is interesting only to developers, not users.

# Repository history

repo has a long history that makes it difficult to discover the canonical repository.

This repository is a fork of Google's https://gerrit.googlesource.com/git-repo/.  It appears that the same code is also served as https://android.googlesource.com/tools/repo/.  These two repository names have given rise to duplicate project names "git-repo" and "tools_repo" ("tools/repo" with '/' replaced with '_').

Due to the [shutdown of Google Code](http://google-opensource.blogspot.com/2015/03/farewell-to-google-code.html0), the original Google Code repo project https://code.google.com/p/git-repo/ has been archived for quite a while now, and is out of date.

## Resyncing with official google repo

This procedure comes to us from the [esrlabs/git-repo](https://github.com/esrlabs/git-repo) project.

For resyncing with the official google repo git, here are the commands for resyncing with the tag v1.12.33 of the official google repo:

    # add google git-repo remote with tag
    git remote add googlesource https://gerrit.googlesource.com/git-repo/
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

Prepare by creating your own GPG keys as described in the
[Pro Git](https://git-scm.com/book) Book
[Signing Your Work](https://git-scm.com/book/id/v2/Git-Tools-Signing-Your-Work) chapter.

Export an ASCII key:

    gpg --armor --export you@example.com > public.txt

Paste this key into file ``repo`` after the other keys.

Again in file ``repo``, Increment the second element of `KEYRING_VERSION`:

    KEYRING_VERSION = (1, 4)

In your Git working copy of `git-repo`, add and commit whatever files you have changed.

Sign the commit:
 
    git tag -s -u KEYID v0.4.16 -m "COMMENT"
    git push origin stable:stable
    git push origin v0.4.16

* For `KEYID`, use the ID of your key.  List your keys using the `gpg --list-keys` command.
* Replace `v0.4.16` With the actual version (note that there are two occurrences of this)
* Replace `COMMENT` with something more illuminating

