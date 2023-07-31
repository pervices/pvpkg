# For a brief overview of the things seen in this file, take a look at support/README.md
VENV=working_env

CLEANUP=working_env
DISTCLEANUP=ship_reports ${CLEANUP}

.PHONY: all

${VENV}:
	python3 -m venv ${VENV} --system-site-packages
	${VENV}/bin/python3 -m pip install -r requirements.txt

clean:
	rm -rf ${CLEANUP}

dist-clean: clean
	rm -rf ${DISTCLEANUP}

report: ${VENV}
	. ${VENV}/bin/activate
	#which python3
	echo ${VENV}/bin/python3 sr_new_file_parse.py
	# -deactivate
	# which python3

all: report
	echo Generating report
	# - deactivate
