#!/usr/bin/env python
"""
Turn the gitenv into RPM spec files which can be built at a later stage.

"""
from __future__ import print_function

import datetime
from glob import glob
import os
import time
import shutil

from git import Repo
import conda.api
import conda.fetch
from conda.resolve import Resolve, MatchSpec

from conda_gitenv.resolve import tempdir, create_tracking_branches

from conda_gitenv.lock import Locked
from conda_gitenv import manifest_branch_prefix

from conda_gitenv.deploy import tags_by_label, tags_by_env

import generate
import install as conda_install

def create_rpmbuild_for_tag(repo, tag_name, target):
    print("CREATE FOR {}".format(tag_name))
    tag = repo.tags[tag_name]
    # Checkout the tag in a detached head form.
    repo.head.reference = tag.commit
    repo.head.reset(working_tree=True)

    # Pull out the environment name from the form "env-<env_name>-<deployed_name>".
    env_name = tag_name.split('-')[1]
    deployed_name = tag_name.split('-', 2)[2]

    manifest_fname = os.path.join(repo.working_dir, 'env.manifest')
    if not os.path.exists(manifest_fname):
        raise ValueError("The tag '{}' doesn't have a manifested environment.".format(tag_name))
    with open(manifest_fname, 'r') as fh:
        manifest = sorted(line.strip().split('\t') for line in fh)

    create_rpmbuild_for_env(manifest, target)

    pkgs = [pkg for _, pkg in manifest]
    name = tag_name.split('-', 1)[1]
    with open(os.path.join(target, 'SPECS', 'SciTools-taggedenv-{}.spec'.format(name)), 'w') as fh:
        fh.write(generate.render_env(name, pkgs))


def create_rpmbuild_for_env(pkgs, target):
    pkg_cache = os.path.join(target, 'SOURCES')
    pkg_names = set(pkg for _, pkg in pkgs)
    if os.path.exists(target):
        # The environment we want to deploy already exists. We should just double check that
        # there aren't already packages in there which we need to remove before we install anything
        # new.
        linked = conda_install.linked(target)
        for pkg in linked:
            if pkg not in pkg_names:
                conda_install.unlink(target, pkg)
    else:
        linked = []

    if set(linked) == pkg_names:
        # We don't need to re-link everything - it is already as expected.
        # The downside is that we are not verifying that each package is installed correctly.
        return

    spec_dir = os.path.join(target, 'SPECS')
    if not os.path.exists(spec_dir):
        os.makedirs(spec_dir)

    for source, pkg in pkgs:
        index = conda.fetch.fetch_index([source], use_cache=True)
        tar_name = pkg + '.tar.bz2'
        pkg_info = index.get(tar_name, None)
        if pkg_info is None:
            raise ValueError('Distribution {} is no longer available in the channel {}.'.format(tar_name, source))
        dist_name = pkg 
        if not conda_install.is_fetched(pkg_cache, dist_name):
            print('Fetching {}'.format(dist_name))
            conda.fetch.fetch_pkg(pkg_info, pkg_cache)
        spec_path = os.path.join(spec_dir, 'SciTools-pkg-' + pkg + '.spec')
        if not os.path.exists(spec_path):
            spec = generate.render_dist_spec(os.path.join(pkg_cache, tar_name))
            with open(spec_path, 'w') as fh:
                fh.write(spec)


def create_rpmbuild_content(repo, target):
    env_tags = tags_by_env(repo)
    for branch in repo.branches:
        # We only want environment branches, not manifest branches.
        if not branch.name.startswith(manifest_branch_prefix):
            manifest_branch_name = manifest_branch_prefix + branch.name
            # If there is no equivalent manifest branch, we need to
            # skip this environment.
            if manifest_branch_name not in repo.branches:
                continue
            manifest_branch = repo.branches[manifest_branch_name]
            branch.checkout()
            labelled_tags = tags_by_label(os.path.join(repo.working_dir, 'labels'))
            # We want to deploy all tags which have a label, as well as the latest tag.
            if env_tags.get(branch.name):
                latest_tag = max(env_tags[branch.name],
                                 key=lambda t: t.commit.committed_date)
                labelled_tags['latest'] = latest_tag.name

            #--------------- New for this ---------

            # Keep track of the labels which have tags - its those we want.
            tags = []
            envs = []
            for label, tag in labelled_tags.items():
                deployed_name = tag.split('-', 2)[2]
                label_target = deployed_name
                label_location = os.path.join(target, branch.name, label)

                env = '{}-{}'.format(branch.name, label)
                tags.append(tag)
                envs.append(env)
                # If we wanted RPMS for each label, enable this.
#                create_rpmbuild_for_label(env, tag, target)
            for tag in tags:
                create_rpmbuild_for_tag(repo, tag, target)


def create_rpm_installer(target, python_spec='python'):
    index = conda.api.get_index()
    matches = Resolve(index).get_pkgs(MatchSpec(python_spec))
    if not matches:
        raise RuntimeError('No python found in the channels.')
    pkg_info = matches[-1].info
    dist_name = '{}-{}-{}'.format(pkg_info['name'], pkg_info['version'], pkg_info['build'])
    pkg_cache = os.path.join(target, 'SOURCES') 
    if not conda_install.is_fetched(pkg_cache, dist_name):
        print('Fetching {}'.format(dist_name))
        conda.fetch.fetch_pkg(pkg_info, pkg_cache)

    installer_source = os.path.join(os.path.dirname(__file__), 'install.py')
    installer_target = os.path.join(pkg_cache, 'install.py')

    shutil.copyfile(installer_source, installer_target)

    specfile = os.path.join(target, 'SPECS', 'SciTools-installer.spec')
    with open(specfile, 'w') as fh:
        fh.write(generate.render_installer(pkg_info))


def configure_parser(parser):
    parser.add_argument('repo_uri', help='Repo to deploy.')
    parser.add_argument('target', help='Location to put the RPMBUILD content.')
    parser.set_defaults(function=handle_args)
    return parser


def handle_args(args):
    with tempdir() as repo_directory:
        repo = Repo.clone_from(args.repo_uri, repo_directory)
        create_tracking_branches(repo)
        create_rpmbuild_content(repo, args.target)
        create_rpm_installer(args.target)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Deploy the tracked environments.')
    configure_parser(parser)
    args = parser.parse_args()
    return args.function(args)


if __name__ == '__main__':
    main()
