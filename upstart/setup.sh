#!/bin/bash
# This script sets up and initializes the daemon script
# that is intended to be run on all target machines
# 
# It moves all files to correct locations, downloads Dacapo suite
# and initializes the service to work on start up.
#
# This script is for a daemon that utilized Ubuntu's Upsart 
# Make sure your distribution supports Upstart

# Checking that it is run with bash
CURRENT=$(pwd)
PROGNAME=$(basename $0)
if [ -z "$BASH_VERSION" ]; then
	echo "${PROGNAME}: Must run with bash."
	exit 1
fi

# Function for exiting upon error
function error_exit
{
	echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	exit 1
}

if [[ $EUID -ne 0 ]]; then
	error_exit "$LINENO: Must run script as root."
fi

# Make sure Upstart is installed
UPSTART=$(dpkg-query -W -f='${Status}\n' upstart)
if [ "${UPSTART}" != "install ok installed" ]; then
	error_exit "$LINENO: Upstart is not installed."
fi	

# Moving all daemon code to /srv/wattsup
DACAPO="http://downloads.sourceforge.net/project/dacapobench/9.12-bach/dacapo-9.12-bach.jar"
DIRECTORY=/srv/wattsup
if [ ! -d "$DIRECTORY" ]; then
	mkdir "$DIRECTORY" || error_exit "$LINENO: Could not create directory: $DIRECTORY"
fi

cd ../
if [ -e "wattdaemon.py" ]; then
	if [ ! -e "$DIRECTORY/wattdaemon.py" ]; then
		cp wattdaemon.py "$DIRECTORY"/wattdaemon.py || error_exit "$LINEON: Could not copy wattdaemon.py"
	fi
else
	error_exit "$LINENO: wattdaemon.py could not be found."
fi

if [ -e "wattsup.py" ]; then
	if [ ! -e "$DIRECTORY/wattsup.py" ]; then
		cp wattsup.py "$DIRECTORY"/wattsup.py || error_exit "$LINEON: Could not copy wattsup.py"
	fi
else
	error_exit "$LINENO: wattsup.py could not be found."
fi

if [ -d "$DIRECTORY" ]; then
	cd "$DIRECTORY" || error_exit "$LINEON: Error moving to: ${DIRECTORY}."
else
	error_exit "$LINEON: Daemon directory ${DIRECTORY} does not exist."
fi

# Download dacapo suite to /srv/wattsup
if [ ! -e "dacapo-9.12-bach.jar" ]; then
	wget "${DACAPO}" || error_exit "$LINEON: Could not download Dacapo benchmark suite."
fi

# Move wattsup.conf to /etc/init
cd "${CURRENT}"
if [ -d "/etc/init" ] && [ -e "wattsup.conf" ]; then
	cp wattsup.conf /etc/init/wattsup.conf || error_exit "$LINEON: Could not copy wattsup.conf"
else
	error_exit "$LINEON: /etc/init not dir or wattsup.conf does not exist."
fi
	
# Initialize the service
initctl reload-configuration || error_exit "$LINEON: initctl reload-configuration failed."

# Start the daemon
service wattsup start || error_exit "$LINEON: Could not start wattsup daemon"

# Check that daemon is running
STATUS=$(service wattsup status)
IFS=' ' read -a values <<< "$STATUS"
if [ "${values[0]}" = "wattsup" ] && [ "${values[1]}" = "start/running," ]; then
	echo "Successfully setup the daemon"
else
	error_exit "$LINEON: Daemon has not successfully started"
fi
exit 0
