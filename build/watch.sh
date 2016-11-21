#!/bin/bash

# nounset: undefined variable outputs error message, and forces an exit
set -u
# errexit: abort script at first error
set -e
# print command to stdout before executing it:
set -x

./node_modules/.bin/budo -d src src/app.js -- -t [ babelify --presets [ es2015 ] ]
