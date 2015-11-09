#!/bin/bash -x
#BUILD HELP DOCS.

cd IMAGE
docker build -t gemini/gemini-docs  .
