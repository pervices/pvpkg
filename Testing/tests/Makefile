# For a brief overview of the things seen in this file, take a look at support/README.md
VENV=report_venv

CLEANUP=*pdf dump/
DISTCLEANUP=report_venv

.PHONY: clean

default-target: report

${VENV}:
	python3 -m venv --system-site-packages ${VENV}
	${VENV}/bin/python3 -m pip install --ignore-installed -r requirements.txt

activate: ${VENV}
	@echo "To activate, manually type: source ${VENV}/bin/activate"

clean:
	rm -rf ${CLEANUP}

dist-clean: clean
	rm -rf ${DISTCLEANUP}

report: ${VENV} 
	@echo "To run report, run: python test_tx_rx_fundamental_frequency.py -s TEST -p t"
	@echo "To override mgmt address: python test_tx_rx_fundamental_frequency.py -s TEST -p t -a 192.168.200.1"
	@echo "For list of product args, type: python test_tx_rx_fundamental_frequency.py -s TEST -p ?"
	@echo ""

#Testing
#test: 
#	$(call xcp,site/crimson)
#	echo TEST1=$(call xcp,site/crimson)
#	Attempt to copy crimson
#	$(${TEST1})
#	TEST=$(call xcp,test,a) 
#	echo "${TEST}"
