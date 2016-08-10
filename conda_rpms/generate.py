import os
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
loader = jinja2.FileSystemLoader(template_dir)

env = jinja2.Environment(loader=loader)

pkg_spec_tmpl = env.get_template('pkg.spec.template')
env_spec_tmpl = env.get_template('env.spec.template')
taggedenv_spec_tmpl = env.get_template('taggedenv.spec.template')
installer_spec_tmpl = env.get_template('installer.spec.template')

import tarfile
import json
import yaml


def render_dist_spec(dist, config):
    with tarfile.open(dist, 'r:bz2') as tar:
        m = tar.getmember('info/index.json')
        fh = tar.extractfile(m)
        import codecs

        reader = codecs.getreader("utf-8")
        pkginfo = json.load(reader(fh))

        try:
            m = tar.getmember('info/recipe.json')
        except KeyError:
            m = None

        if m:
            fh = tar.extractfile(m)
            meta = yaml.safe_load(reader(fh))
        else:
            meta = {}

    meta_about = meta.setdefault('about', {})
    meta_about.setdefault('license', pkginfo.get('license'))
    meta_about.setdefault('summary', 'The {} package'.format(pkginfo['name']))

    rpm_prefix = config['rpm']['prefix']
    install_prefix = config['install']['prefix']

    return pkg_spec_tmpl.render(pkginfo=pkginfo,
                                meta=meta,
                                rpm_prefix=rpm_prefix,
                                install_prefix=install_prefix)

def render_env(branch_name, label, repo, config, tag, commit_num):
    env_info = {'url': 'http://link/to/gh',
                'name': branch_name,
		'label' : label,
                'summary': 'A SciTools environment.',
                'version': commit_num,}
    install_prefix = config['install']['prefix']
    rpm_prefix = config['rpm']['prefix']
    return env_spec_tmpl.render(install_prefix=install_prefix,
                                rpm_prefix=rpm_prefix, env=env_info,
                                labelled_tag=tag.split('-')[-1])


def render_taggedenv(env_name, tag, pkgs, config, env_spec):
    env_info = {'url': 'http://link/to/gh',
                'name': env_name,
                'tag': tag,
                'summary': 'An environment in which to rejoice.',
                'version': '1',
                'spec': '\n'.join(env_spec)}
    rpm_prefix = config['rpm']['prefix']
    install_prefix = config['install']['prefix']
    return taggedenv_spec_tmpl.render(install_prefix=install_prefix,
                                      pkgs=pkgs,
                                      rpm_prefix=rpm_prefix,
                                      env=env_info)


def render_installer(pkg_info, config):
    rpm_prefix = config['rpm']['prefix']
    install_prefix = config['install']['prefix']
    return installer_spec_tmpl.render(install_prefix=install_prefix,
                                      rpm_prefix=rpm_prefix,
                                      pkg_info=pkg_info)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("distribution")
    args = parser.parse_args()
    #print(render_dist_spec(args.distribution))
    #print(render_env('my_second_env', pkgs=['udunits2-2.2.20-0']))
    print(args)
    print(render_installer({'name': 'python', 'version': '2.11.1',
                            'build': '0'}))
