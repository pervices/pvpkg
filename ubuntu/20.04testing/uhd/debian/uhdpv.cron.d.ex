#
# Regular cron jobs for the uhdpv package
#
0 4	* * *	root	[ -x /usr/bin/uhdpv_maintenance ] && /usr/bin/uhdpv_maintenance
