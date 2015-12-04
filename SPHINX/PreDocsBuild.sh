#!/bin/bash -x

rm -rf docs

git clone https://github.com/Gemini-sys/docs.git

cd docs/webdocs/

cp -rf * IMAGE\source\*
