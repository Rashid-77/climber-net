#!/usr/bin/env bash

set -e
set -x

pytest --capture=tee-sys tests/ "${@}"
