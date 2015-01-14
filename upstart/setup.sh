#!/bin/bash
# This script sets up and initializes the daemon script
# that is intended to be run on all target machines
# 
# It moves all files to correct locations, downloads Dacapo suite
# and initializes the service to work on start up.
#
# This script is for a daemon that utilized Ubuntu's Upsart 
# Make sure your distribution supports Upstart
# 
# This script also sets the environtment vairables: DB_HOST,
# DB_USERNAME, DB_PASS and DB_HOST by prompting the user.
# These are used to access your MySQL server.

# ---------------------------------------------------------
# Checking requirements are met for running this script
# Setting up...
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Moving all daemon code to proper location. Currently set 
# to be /lib/wattsup
# ---------------------------------------------------------

DACAPO="http://downloads.sourceforge.net/project/dacapobench/9.12-bach/dacapo-9.12-bach.jar"
DIRECTORY=/lib/wattsup

# Making the 'wattsup' directory.
if [ ! -d "$DIRECTORY" ]; then
	mkdir "$DIRECTORY" || error_exit "$LINENO: Could not create directory: $DIRECTORY"
fi

cd ../

# Moving wattdaemon to proper location.
if [ -e "wattdaemon.py" ]; then
	if [ ! -e "$DIRECTORY/wattdaemon.py" ]; then
		cp wattdaemon.py "$DIRECTORY"/wattdaemon.py || error_exit "$LINEON: Could not copy wattdaemon.py"
	fi
else
	error_exit "$LINENO: wattdaemon.py could not be found."
fi

# Moving wattsup to proper location.
if [ -e "wattsup.py" ]; then
	if [ ! -e "$DIRECTORY/wattsup.py" ]; then
		cp wattsup.py "$DIRECTORY"/wattsup.py || error_exit "$LINEON: Could not copy wattsup.py"
	fi
else
	error_exit "$LINENO: wattsup.py could not be found."
fi

# Moving dacapo.py to proper location.
if [ -e "dacapo.py" ]; then
	if [ ! -e "$DIRECTORY/dacapo.py" ]; then
		cp dacapo.py "$DIRECTORY"/dacapo.py || error_exit "$LINEON: Could not copy dacapo.py"
	fi
else
	error_exit "$LINENO: dacapo.py could not be found."
fi

# Changing in to the new directory.
if [ -d "$DIRECTORY" ]; then
	cd "$DIRECTORY" || error_exit "$LINEON: Error moving to: ${DIRECTORY}."
else
	error_exit "$LINEON: Daemon directory ${DIRECTORY} does not exist."
fi

# Download dacapo suite to /lib/wattsup
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

# ---------------------------------------------------------
# Setting up compliance with the database
# ---------------------------------------------------------

# The checks for variable already being set are not 100% correct.
# Should fix in the near future.

# Setting up the environment variables for DB
if [ -z "$DB_HOST" ]; then
    echo Enter energy database hostname:
    read HOST
    export DB_HOST="$HOST"
fi

# Setting up env for db username
if [ -z "$DB_USERNAME" ]; then
    echo Enter energy database username:
    read USERN
    export DB_USERNAME="$USERN"
fi

# Setting up env for user password on database
if [ -z "$DB_PASS" ]; then
    echo "Enter energy db password for $DB_USERNAME:"
    read PASS
    export $DB_PASS="$PASS"
fi

# Setting up db name to use
if [ -z "$BD_NAME" ]; then
    echo Enter energy db name:
    read NAME
    export DB_NAME="$NAME"
fi

# Run the database setup script (dbsetup.py)
./dbsetup.py
# Add machine to the database
./minsert.py

# ---------------------------------------------------------
# Initializing and starting the daemon service
# ---------------------------------------------------------

# Initializing...
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
