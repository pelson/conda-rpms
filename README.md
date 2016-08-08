Create RPMs from a conda-gitenv
===============================

conda-rpms is designed to convert a resolved [conda-gitenv](https://github.com/SciTools/conda-gitenv) environment into a collection of RPM specs suitable for deployment on compatible platforms (Red Hat Enterprise Linux, Fedora, etc.).

A high level description of the motivation for the creation of RPMs from a [conda-gitenv](https://github.com/SciTools/conda-gitenv) is described in the [centrally managed scientific software workflow](https://rawgit.com/pelson/conda-rpms/master/tmp_overview_docs/scitools-env-workflow.html) document.

To transform the conda distribution to RPM specs, conda-rpms uses tools including git-python, Jinja and conda.

Because a built RPM knows its destined installation location, a number of RPM abstractions have been made that enable us to retain conda's hard-linking and relocatability benefits.


Usage
=====

There are two conda-rpms command entrypoints.

`python -m conda_rpms.build_rpm_structure` creates the RPM specs and sources. 

`python -m conda_rpms.build` is a general purpose rpmbuild wrapper that inspects the RPM build directory for RPMs that have already been built, and then builds those that haven't. This is a general purpose tool that has nothing to do with conda - if you are aware of such a tool already existing, please raise an issue let us know! `;)`


RPM Types
=========

Package RPM
-----------

RPM name format: ``<RPM prefix>-pkg-<pkg name>-<pkg version>-<pkg build id>``

A package RPM represents the conda "package cache" (the thing that normally lives in `<root prefix>/.pkgs/<pkg name>-<pkg version>-<pkg build id>`).
A package RPM *does not* express its dependencies and can not be usefully installed as a standalone entity.

Tagged environment RPM
----------------------

RPM name format: ``<RPM prefix>-env-<env name>-tag-<env tag>``

A tagged environment RPM represents a resolved conda environment.
It depends on all Package RPMs that should be installed in order to produce a working environment. The tagged environment RPM knows its target installation prefix, and uses conda functionality at install time to link the Package RPMs to the desired installation prefix.

Labelled environment RPM
------------------------

RPM name format: `<RPM prefix>-env-<env name>-label-<label>`

A labelled environment is simply a meta package which depends on one, and only one, Tagged Environment RPM.
Unlike the immutable tagged environment, a labelled environment will tend to change to reference newer tags as time moves on.
This change is reflected in the labelled environment's `version`, meaning that it is only possible to ever have one labelled environment RPM installed per environment name.


conda-rpms without conda-gitenv
===============================

In some situations, it would be valuable to be able to produce RPMs from a standard conda yaml environment definition, rather than through conda-gitenv.
Whilst we haven't yet implemented this obvious feature, it shouldn't be much of an extension to the existing codebase, and PRs would be happily received.

