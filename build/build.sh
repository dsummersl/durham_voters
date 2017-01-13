#!/bin/bash

# nounset: undefined variable outputs error message, and forces an exit
set -u
# errexit: abort script at first error
set -e
# print command to stdout before executing it:
set -x

mkdir out || true

cp -r src/* out
./node_modules/.bin/browserify src/app.js  -o out/app.js -t browserify-css -t [ babelify --presets [ es2015 ] ] -g yo-yoify -g uglifyify
