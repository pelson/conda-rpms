"""
Build all spec files which exists and which don't already have
equivalent built RPMs in the build directory.

"""
import os
import glob
import subprocess


def name_version_release(spec_fh):
    """
    Take the name, version and release number from the given filehandle pointing at a sepc file.
    """
    content = {}
    for line in spec_fh:
        if line.startswith('Name:') and 'name' not in content:
            content['name'] = line[5:].strip()
        elif line.startswith('Version:') and 'version' not in content:
            content['version'] = line[8:].strip()
        elif line.startswith('Release:') and 'release' not in content:
            content['release'] = line[8:].strip()
    return content


def build_new(rpmbuild_dir, rpm_directory):
    """We rely on spec naming conventions to check that the build RPMs actually exist."""
    specs_directory = os.path.join(rpmbuild_dir, 'SPECS')
    sources_directory = os.path.join(rpmbuild_dir, 'SOURCES')
    for spec in sorted(glob.glob(os.path.join(specs_directory, '*.spec'))):
        spec_path = os.path.join(specs_directory, spec)
        rpm_name = spec[:-5]
        with open(spec_path, 'r') as fh:
            spec_info = name_version_release(fh)
        rpm_name = '{name}-{version}-{release}.x86_64.rpm'.format(**spec_info)

        if not os.path.exists(os.path.join(rpm_directory, rpm_name)):
            subprocess.check_call(['rpmbuild', '-bb', '--define', "_topdir {}".format(rpmbuild_dir),
                                   spec_path, '--force'])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('rpmbuild_dir', help='The location of the rpmbuild directory.')
    parser.add_argument('rpm_dir', help='The location to look for existing RPMs.')

    args = parser.parse_args()

    build_new(args.rpmbuild_dir, args.rpm_dir)

