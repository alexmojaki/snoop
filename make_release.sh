#!/usr/bin/env bash

set -eux -o pipefail

if [ ! -z "$(git status --porcelain)" ]; then
    set +x
    echo You have uncommitted changes which would mess up the git tag
    exit 1
fi

if [ -z "${1+x}" ]; then
    set +x
    echo Provide a version argument
    echo "${0} <major>.<minor>.<patch>"
    exit 1
fi

if [[ ! ${1} =~ ^([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$ ]]; then
    echo "Not a valid release tag."
    exit 1
fi

tox -p 3

export TAG="v${1}"
git tag "${TAG}"
git push origin HEAD "${TAG}"
rm -rf ./build ./dist
python -m build --sdist --wheel .
twine upload ./dist/*.whl dist/*.tar.gz
