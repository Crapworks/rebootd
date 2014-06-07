#!/usr/bin/env bash

#
# This file is used to build a debain package in jenkins
#

# create temporary directory
TMPDIR=`mktemp -d -u`

# adjust changelog
DISTRIBUTION=$1
VERSION=`./rebootd.py --version 2>&1`
debchange --newversion ${VERSION} --distribution ${DISTRIBUTION} --force-distribution -m "released version ${VERSION} for ${DISTRIBUTION}"

# create build environment
mkdir -p deb

# copy workspace to deb/workspace
cp -a ${WORKSPACE} ${TMPDIR}
mv ${TMPDIR} deb/workspace

# build package in build dir
cd deb/workspace
debuild -i -us -uc -b

# go pack to workspace
cd ${WORKSPACE}
