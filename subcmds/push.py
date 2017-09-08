#
# Copyright (C) 2008 The Android Open Source Project
# Copyright (C) 2017 Wave Computing, Inc.  John McGehee
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import copy
import re
import sys

from command import InteractiveCommand
from editor import Editor
from error import HookError, UploadError
from git_command import GitCommand
from project import RepoHook
from subcmds.upload import Upload

from pyversion import is_python3
# pylint:disable=W0622
if not is_python3():
  input = raw_input
else:
  unicode = str
# pylint:enable=W0622

UNUSUAL_COMMIT_THRESHOLD = 5

class Push(Upload):
  GERRIT = False
  common = True
  helpSummary = "Push changes to remote"
  helpUsage = """
%prog [--re --cc] [<project>]...
"""
  helpDescription = """
TODO: Modify for `repo push`.

The '%prog' command is used to send changes to the Gerrit Code
Review system.  It searches for topic branches in local projects
that have not yet been published for review.  If multiple topic
branches are found, '%prog' opens an editor to allow the user to
select which branches to upload.

'%prog' searches for uploadable changes in all projects listed at
the command line.  Projects can be specified either by name, or by
a relative or absolute path to the project's local directory. If no
projects are specified, '%prog' will search for uploadable changes
in all projects listed in the manifest.

If the --reviewers or --cc options are passed, those emails are
added to the respective list of users, and emails are sent to any
new users.  Users passed as --reviewers must already be registered
with the code review system, or the upload will fail.

Configuration
-------------

review.URL.autoupload:

To disable the "Upload ... (y/N)?" prompt, you can set a per-project
or global Git configuration option.  If review.URL.autoupload is set
to "true" then repo will assume you always answer "y" at the prompt,
and will not prompt you further.  If it is set to "false" then repo
will assume you always answer "n", and will abort.

review.URL.autoreviewer:

To automatically append a user or mailing list to reviews, you can set
a per-project or global Git option to do so.

review.URL.autocopy:

To automatically copy a user or mailing list to all uploaded reviews,
you can set a per-project or global Git option to do so. Specifically,
review.URL.autocopy can be set to a comma separated list of reviewers
who you always want copied on all uploads with a non-empty --re
argument.

review.URL.username:

Override the username used to connect to Gerrit Code Review.
By default the local part of the email address is used.

The URL must match the review URL listed in the manifest XML file,
or in the .git/config within the project.  For example:

  [remote "origin"]
    url = git://git.example.com/project.git
    review = http://review.example.com/

  [review "http://review.example.com/"]
    autoupload = true
    autocopy = johndoe@company.com,my-team-alias@company.com

review.URL.uploadtopic:

To add a topic branch whenever uploading a commit, you can set a
per-project or global Git option to do so. If review.URL.uploadtopic
is set to "true" then repo will assume you always want the equivalent
of the -t option to the repo command. If unset or set to "false" then
repo will make use of only the command line option.

References
----------

Gerrit Code Review:  http://code.google.com/p/gerrit/

"""

  def _Options(self, p):
    p.add_option('-t',
                 dest='auto_topic', action='store_true',
                 help='Send local branch name to Gerrit Code Review')
    p.add_option('--re', '--reviewers',
                 type='string',  action='append', dest='reviewers',
                 help='Request reviews from these people.')
    p.add_option('--cc',
                 type='string',  action='append', dest='cc',
                 help='Also send email to these email addresses.')
    p.add_option('--br',
                 type='string',  action='store', dest='branch',
                 help='Branch to upload.')
    p.add_option('--cbr', '--current-branch',
                 dest='current_branch', action='store_true',
                 help='Upload current git branch.')
    p.add_option('-d', '--draft',
                 action='store_true', dest='draft', default=False,
                 help='If specified, upload as a draft.')
    p.add_option('-p', '--private',
                 action='store_true', dest='private', default=False,
                 help='If specified, upload as a private change.')
    p.add_option('-w', '--wip',
                 action='store_true', dest='wip', default=False,
                 help='If specified, upload as a work-in-progress change.')
    p.add_option('-D', '--destination', '--dest',
                 type='string', action='store', dest='dest_branch',
                 metavar='BRANCH',
                 help='Submit for review on this target branch.')

    # Options relating to upload hook.  Note that verify and no-verify are NOT
    # opposites of each other, which is why they store to different locations.
    # We are using them to match 'git commit' syntax.
    #
    # Combinations:
    # - no-verify=False, verify=False (DEFAULT):
    #   If stdout is a tty, can prompt about running upload hooks if needed.
    #   If user denies running hooks, the upload is cancelled.  If stdout is
    #   not a tty and we would need to prompt about upload hooks, upload is
    #   cancelled.
    # - no-verify=False, verify=True:
    #   Always run upload hooks with no prompt.
    # - no-verify=True, verify=False:
    #   Never run upload hooks, but upload anyway (AKA bypass hooks).
    # - no-verify=True, verify=True:
    #   Invalid
    p.add_option('--no-cert-checks',
                 dest='validate_certs', action='store_false', default=True,
                 help='Disable verifying ssl certs (unsafe).')
    p.add_option('--no-verify',
                 dest='bypass_hooks', action='store_true',
                 help='Do not run the upload hook.')
    p.add_option('--verify',
                 dest='allow_all_hooks', action='store_true',
                 help='Run the upload hook without prompting.')

