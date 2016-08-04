#!/usr/bin/env bash

REPO_ROOT=$(cd "$(dirname "$0")/.."; pwd;)

# Test conda-gitenv approach.
cat << EOF | docker run -i \
                        -v ${REPO_ROOT}:/repo \
                        -a stdin -a stdout -a stderr \
                        centos:6 \
                        bash || exit $?

yum install -y rpm-build createrepo tar

rpmbuild -bb --define "_sourcedir /repo/tests/output/gitenv_rpmbuild/SOURCES" /repo/tests/output/gitenv_rpmbuild/SPECS/*.spec --force

# Put the RPMs in a nice place so we can look at them.
cp -r /root/rpmbuild/RPMS/ /repo/tests/output/gitenv_rpmbuild/

createrepo /repo/tests/output/gitenv_rpmbuild/RPMS/

rm -rf /etc/yum.repos.d/*

cat << YUMREPO_EOF > /etc/yum.repos.d/myrepo.repo

[myrepo]
name = My local repo
baseurl = file:///repo/tests/output/gitenv_rpmbuild/RPMS/
gpgcheck=0

YUMREPO_EOF

yum install -y TestMyBuild-env-*

# TODO: Make some assertions!?

EOF

