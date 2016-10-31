# Global environment related to builds
# Things to store
# - Defaults (which can be overridden)
# - External services (Docker registry)
# 
export APPORBIT_SHA1=$(git log --pretty=format:'%h' -n 1)
export APPORBIT_BRANCH=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')
# export APPORBIT_VERSION=0.1-${APPORBIT_SHA1}-${APPORBIT_BRANCH}
export APPORBIT_VERSION=0.1
export APPORBIT_ALTVER=latest
export APPORBIT_TAGUSER=apporbit
export APPORBIT_TAGPRE=

