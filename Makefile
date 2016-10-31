BASEDIR := ${PWD}
SRCDIR := ${BASEDIR}/cicd/src
BUILDDIR := ${BASEDIR}/cicd/build
APPORBIT_VERSION := 2.0-beta
APPORBIT_ALTVER := latest
APPORBITUSER := apporbit
APPORBIT_TAGPRE :=
APPORBIT_REGISTRY := jenkin-registry.gsintlab.com/
APPORBIT_PUSHPRE := ${APPORBIT_REGISTRY}${APPORBITUSER}
CSRCDIR := /go/src/appos:ro,z
COMPILE := ${APPORBITUSER}/apporbit-compile

# Following modules are built with Platform Build in Jenkins
DEFAULT_MODULES := cicd/src/apporbit-server cicd/apporbit-rmq cicd/apporbit-chef 
MODULES := ${DEFAULT_MODULES}
COMPILE_MODULES := ${MODULES}
IMAGE_MODULES := ${MODULES} 

TEST_MODULES := 
COUTDIR := /go/bin

DRUN = docker run --rm -i
DBUILD = docker build
DPUSH = docker push
DTAG = docker tag

GOTEST = go test -v

IGNORE := $(shell bash -c "source ${SRCDIR}/setup/setenv.sh; env | sed 's/=/:=/' | sed 's/^/export /' > ${BUILDDIR}/makeenv")
include ${BUILDDIR}/makeenv


.PHONY: setup clean
default: clean compile images

all: clean compile images 

setup:

	${DBUILD} -f ${SRCDIR}/common/compile/Dockerfile \
	          -t ${APPORBITUSER}/apporbit-compile ${SRCDIR}/common/compile

clean:

	${DRUN} -v ${BUILDDIR}:${COUTDIR}:z ${COMPILE} sh -c 'rm -rf ${COUTDIR}/*'

compile: setup

	for module in ${COMPILE_MODULES} ; do \
	    basemodule=$$(basename $$module) ;\
	    echo "Compiling $$module using $$basemodule ..." ;\
            mkdir -p ${BUILDDIR}/$$basemodule; \
            ${DRUN} -e OUTPUTNAME="$$basemodule" -v ${BASEDIR}/$$module:${CSRCDIR} \
			-v ${BUILDDIR}/$$basemodule:${COUTDIR}:z ${COMPILE} ;\
	done

images:

	${DBUILD}  -t ${APPORBITUSER}/common ${SRCDIR}/common/runtime

	for module in ${IMAGE_MODULES} ; do \
	    basemodule=$$(basename $$module) ;\
		if [ -f ${BUILDDIR}/$$basemodule/Dockerfile ] ; then \
	    ${DBUILD}  -t ${APPORBITUSER}/$$basemodule ${BUILDDIR}/$$basemodule ;\
		fi ;\
	done

test:

	for module in ${TEST_MODULES} ; do \
	    basemodule=$$(basename $$module) ;\
		printf "\n==> Starting Test on $$module \n";\
                cd ${BUILDDIR}/$$basemodule ; \
                 ${GOTEST} ; \
		echo "==> Test Execution completed on $$module";\
        done

install:

	for IMG in ${MODULES} ; do \
	    BASEIMG=$(basename $$IMG) ;\
		${DTAG}  ${APPORBITUSER}/$$BASEIMG ${APPORBIT_PUSHPRE}/$$BASEIMG:${APPORBIT_VERSION} ;\
		${DTAG} -f ${APPORBITUSER}/$$BASEIMG ${APPORBIT_PUSHPRE}/$$BASEIMG:${APPORBIT_ALTVER} ;\
		${DPUSH} ${APPORBIT_PUSHPRE}/$$BASEIMG:${APPORBIT_VERSION} ;\
		${DPUSH} ${APPORBIT_PUSHPRE}/$$BASEIMG:${APPORBIT_ALTVER} ;\
	done



