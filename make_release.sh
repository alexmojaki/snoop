#!/usr/bin/env bash

set -eux

rm -rf dist/* build/*
python setup.py sdist
twine upload dist/*