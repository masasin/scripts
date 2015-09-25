#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Automate merging of git branches
# Copyright © 2015 Jean Nassar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__doc__="""
File: {name}
Author: Jean Nassar
Email: jeannassar5@gmail.com
Github: https://github.com/masasin
Description: Automate merging of git branches

Note that the default upstream branch is develop.

This code uses docopt and sh, both of which can be downloaded from PyPi. It is
compatible with Python versions 2 and 3.

Inspired by: http://www.jperla.com/blog/post/a-clean-python-shell-script

Usage:
    {name} -u | -b [--upstream=<branch>]
    {name} -h | --help
    {name} --version

Options:
    -h --help                Show this screen.
    --version                Show version.
    -u --merge-upstream      Merge the latest upstream into the current branch.
    -b --merge-branch        Merge the current branch into upstream; force -u.
    -U --upstream=<branch>   The branch to be merged. [default: develop]

""".format(name=__file__)
__version__ = "0.1"

import re
import logging

from docopt import docopt
import sh
from sh import git


class MergerError(Exception):
    pass


def main():
    args = docopt(__doc__, version=__version__)

    upstream = args["--upstream"]
    current = get_current_branch()

    if args["--merge-upstream"]:
        merge_upstream(upstream, current)
    elif args["--merge-branch"]:
        merge_branch(upstream, current)


def get_current_branch():
    """
    Get the current branch.

    Raises
    ------
    RuntimeError
        If the git status could not be obtained (e.g. the directory is not a git
        repository).
    MergerError
        If there are changes to be committed.

    """
    try:
        status = str(git("status"))
    except sh.ErrorReturnCode as e:
        raise RuntimeError(e.stderr.decode())

    match = re.match("On branch (\w+)", status)
    current = match.group(1)

    logging.info("In {curr} branch".format(curr=current))

    if status.endswith("nothing to commit, working directory clean\n"):
        logging.debug("Directory clean in {} branch".format(current))
    else:
        raise MergerError("Directory not clean, must commit:\n"
                          "{status}".format(status=status))
    return current


def merge_upstream(upstream, current):
    """
    Merge the latest upstream into the current branch.

    Parameters
    ----------
    upstream : str
        The name of the branch to be merged.
    current : str
        The name of the current branch

    Raises
    ------
    RuntimeError
        If the upstream and current branches are identical.
    MergerError
        If a branch cannot be brought up to date.

    """
    if current == upstream:
        raise RuntimeError("You must be in the branch you want to merge, "
                           "not the upstream branch ({}).".format(upstream))

    logging.info("Switching to {upstream} branch".format(upstream=upstream))
    git("checkout", upstream)
    git("pull")
    logging.info("Pulled latest changes from origin into {}".format(upstream))
    logging.debug("Ensuring {} has the latest changes".format(upstream))
    pull_result = git("pull")
    if "up-to-date" in pull_result:
        logging.debug("Local copy up-to-date")
    else:
        raise MergerError("Local copy of {upstream} was not up to date:\n"
                          .format(upstream)
                          + "{pull_result}".format(pull_result=pull_result))

    logging.info("Switching back to {curr} branch".format(curr=current))
    git("checkout", current)
    git("merge", upstream)
    logging.info("Merged latest {upstream} changes into {curr} branch"
                 .format(upstream=upstream, curr=current))
    logging.debug("Ensuring latest {upstream} changes in {curr} branch"
                  .format(upstream=upstream, curr=current))
    merge_result = git("merge", upstream)
    if "up-to-date" in merge_result:
        logging.debug("{curr} branch is up-to-date".format(curr=current))
    else:
        raise MergerError("{curr} branch not up to date:\n".format(curr=current)
                          + "{merge_result}".format(merge_result=merge_result))
    logging.info("Successfully merged {upstream} branch into {curr} branch!"
                 .format(upstream=upstream, curr=current))


def merge_branch(upstream, current):
    """
    Merge the the current branch into upstream and pushes to remote.

    Note that this operation merges upstream into the current branch first, and
    that the branch is deleted before the push to remote.

    Parameters
    ----------
    upstream : str
        The name of the branch to be merged.
    current : str
        The name of the current branch

    Raises
    ------
    RuntimeError
        If the upstream and current branches are identical.
    MergerError
        If the remote repository cannot be brought up to date.

    """
    if current == upstream:
        raise RuntimeError("You must be in the branch you want to merge, "
                           "not the upstream branch ({}).".format(upstream))

    merge_upstream(upstream, current)
    logging.info("Switching to {upstream} branch".format(upstream=upstream))
    git("checkout", upstream)
    git("merge", current)
    logging.info("Merged latest {curr} changes into {upstream} branch"
                 .format(curr=current, upstream=upstream))

    git("branch", "-d", current)
    logging.info("Safely deleted {curr}".format(curr=current))

    git("push")
    logging.info("Pushed {upstream} to origin".format(upstream=upstream))
    logging.debug("Ensuring that origin has latest {}".format(upstream))
    push_result = git("push")
    if "up-to-date" in push_result:
        logging.debug("Remote repository is up-to-date: {}".format(upstream))
    else:
        raise MergerError("Remote repository is not up to date:\n{push_result}"
                          .format(push_result=push_result))
    logging.info("Successfully merged {curr} into {upstream} "
                 .format(curr=current, upstream=upstream)
                 + "and pushed to origin!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
