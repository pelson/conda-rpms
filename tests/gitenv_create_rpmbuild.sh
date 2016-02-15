#!/usr/bin/env bash

REPO_ROOT=$(cd "$(dirname "$0")/.."; pwd;)

# Test conda-gitenv approach.
cat << EOF | docker run -i \
                        -v ${REPO_ROOT}:/repo \
                        -a stdin -a stdout -a stderr \
                        centos:6 \
                        bash || exit $?

yum install -y rpm-build createrepo wget which tar git
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-verbose
bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && rm -f Miniconda*.sh
export PATH=/opt/conda/bin:$PATH

export PYTHONPATH=/repo/

rm -rf /opt/conda/pkgs/
mkdir -p /repo/tests/output/pkg_cache
ln -s /repo/tests/output/pkg_cache /opt/conda/pkgs

conda install --yes -c conda-forge gitpython conda-build-all

git clone https://github.com/SciTools/conda-gitenv.git
cd conda-gitenv
python setup.py install
cd ..

mkdir -p /repo/tests/output

export ENV_REPO=/repo/tests/output/gitenv
mkdir -p /repo/tests/output/gitenv
cd /repo/tests/output/gitenv
git init
git checkout -b default
cat <<SPEC_EOF > env.spec
channels:
 - defaults
env: 
 - python

SPEC_EOF

git add env.spec
git commit -m "Added the default environment."

/opt/conda/bin/conda-gitenv resolve /repo/tests/output/gitenv
/opt/conda/bin/conda-gitenv autotag /repo/tests/output/gitenv

python /repo/conda_rpms/build_rpm_structure.py /repo/tests/output/gitenv /repo/tests/output/gitenv_rpmbuild

EOF

