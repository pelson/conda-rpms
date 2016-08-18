#!/usr/bin/env bash

export OUTDIR=/repo/tests/output
export ENV_REPO=${OUTDIR}/gitenv
export INSTALL_ROOT=/opt/conda

REPO_ROOT=$(cd "$(dirname ${0})/../../.."; pwd;)

# Test conda-gitenv approach.
cat << EOF | docker run -i \
                        -v ${REPO_ROOT}:/repo \
                        -a stdin -a stdout -a stderr \
                        centos:6 \
                        bash || exit ${?}

yum install -y rpm-build wget which tar
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh --no-verbose
bash Miniconda3-latest-Linux-x86_64.sh -b -p ${INSTALL_ROOT} && rm -f Miniconda*.sh
export PATH=${INSTALL_ROOT}/bin:\${PATH}

export PYTHONPATH=/repo/

rm -rf ${INSTALL_ROOT}/pkgs/
mkdir -p ${OUTDIR}/pkg_cache
ln -s ${OUTDIR}/pkg_cache /opt/conda/pkgs

conda install --yes -c conda-forge gitpython conda-build-all git


git config --global user.email "you@example.com"
git config --global user.name "Your Name"


git clone https://github.com/SciTools/conda-gitenv.git
cd conda-gitenv
python setup.py install
cd ..

mkdir -p ${OUTDIR} ${ENV_REPO}
cd ${ENV_REPO}
git init
cat <<SPEC_EOF > env.spec
channels:
 - defaults
env: 
 - python

SPEC_EOF

git add env.spec
git commit -m "Added the default environment."
git branch -m default

conda-gitenv resolve ${OUTDIR}/gitenv
conda-gitenv autotag ${OUTDIR}/gitenv


# Label the resolved tag
ENV_TAG=\$(cd ${OUTDIR}/gitenv; git tag -l | grep default | head -n 1)
echo "ENV TAG: \${ENV_TAG}"
git checkout default
mkdir -p labels
echo \${ENV_TAG} > labels/current.txt
git add labels/current.txt
git commit -m "Added the current label to the default environment."

cat <<CONFIG_EOF > /repo/conda_rpms/config.yaml
rpm:
    prefix: 'TestMyBuild'

install:
    prefix: '/opt/testmybuild'

CONFIG_EOF

python /repo/conda_rpms/build_rpm_structure.py ${OUTDIR}/gitenv ${OUTDIR}/gitenv_rpmbuild -c /repo/conda_rpms/config.yaml

test -f ${OUTDIR}/gitenv_rpmbuild/SPECS/TestMyBuild-installer.spec

EOF

