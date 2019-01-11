#!/usr/bin/env python3

import collections
import re
import os
import zipfile
import json

pfx = "write_profile:"

VERSION_FILE = "profile/version.txt"

# Create a dynamic NLS file with the mapping between application ID and
# application names.

def write_profile(logger, app_map):
    sd = get_server_data(logger)
    if sd is False:
        logger.error("Unable to complete without server data...")
        return False

    logger.info("{0} Writing profile/nls/en_us.txt".format(pfx))
    if not os.path.exists("profile/nls"):
        try:
            os.makedirs("profile/nls")
        except:
            LOGGER.error('unable to create node NLS directory.')

    try:
        nls = open("profile/nls/en_us.txt", "w")

        # Write out the standard node, command, and status entries

        nls.write("# controller\n")
        nls.write("ND-Roku-NAME = Roku Media Player\n")
        nls.write("ND-Roku-ICON = Output\n")
        nls.write("ST-ctl-ST-NAME = NodeServer Online\n")
        nls.write("ST-ctl-GV0-NAME = Active application id\n")
        nls.write("ST-ctl-GV1-NAME = Active application name\n")
        nls.write("CMD-ctl-HOME-NAME = Home\n")
        nls.write("CMD-ctl-REV-NAME = Reverse\n")
        nls.write("CMD-ctl-FWD-NAME = Forward\n")
        nls.write("CMD-ctl-PLAY-NAME = Play\n")
        nls.write("CMD-ctl-SELECT-NAME = Select\n")
        nls.write("CMD-ctl-LEFT-NAME = Left\n")
        nls.write("CMD-ctl-RIGHT-NAME = Right\n")
        nls.write("CMD-ctl-DOWN-NAME = Down\n")
        nls.write("CMD-ctl-UP-NAME = Up\n")
        nls.write("CMD-ctl-BACK-NAME = Back\n")
        nls.write("CMD-ctl-REPLAY-NAME = InstantReplay\n")
        nls.write("CMD-ctl-INFO-NAME = Info\n")
        nls.write("CMD-ctl-BACKSPACE-NAME = Backspace\n")
        nls.write("CMD-ctl-SEARCH-NAME = Search\n")
        nls.write("CMD-ctl-ENTER-NAME = Enter\n")
        nls.write("\n")
        nls.write("# Launch application node\n")
        nls.write("ND-Application-NAME = Launcher\n")
        nls.write("ND-Application-ICON = Output\n")
        nls.write("CMD-app-LAUNCH-NAME = Launch it\n")
        nls.write("\n")
        nls.write("EN_APP-0 = Screensaver\n")

        # write out the mapping
        for appid in app_map:
            nls.write("EN_APP-%s = %s\n" % (appid, app_map[appid][0]))

        nls.write("EN_APP_NUM-0 = Screensaver\n")
        for appid in app_map:
            nls.write("EN_APP_NUM-%d = %s\n" % (app_map[appid][1], app_map[appid][0]))

        nls.close()
    except:
        LOGGER.error('Failed to write node NLS file.')

    # Update the profile version file with the info from server.json
    with open(VERSION_FILE, 'w') as outfile:
        outfile.write(sd['profile_version'])
    outfile.close()

    # Create the zip file that can be uploaded to the ISY
    write_profile_zip(logger)

    logger.info(pfx + " done.")


def write_profile_zip(logger):
    src = 'profile'
    abs_src = os.path.abspath(src)
    with zipfile.ZipFile('profile.zip', 'w') as zf:
        for dirname, subdirs, files in os.walk(src):
            # Ignore dirs starint with a dot, stupid .AppleDouble...
            if not "/." in dirname:
                for filename in files:
                    if filename.endswith('.xml') or filename.endswith('txt'):
                        absname = os.path.abspath(os.path.join(dirname, filename))
                        arcname = absname[len(abs_src) + 1:]
                        logger.info('write_profile_zip: %s as %s' %
                                (os.path.join(dirname, filename), arcname))
                        zf.write(absname, arcname)
    zf.close()


def get_server_data(logger):
    # Read the SERVER info from the json.
    try:
        with open('server.json') as data:
            serverdata = json.load(data)
    except Exception as err:
        logger.error('get_server_data: failed to read {0}: {1}'.format('server.json',err), exc_info=True)
        return False
    data.close()
    # Get the version info
    try:
        version = serverdata['credits'][0]['version']
    except (KeyError, ValueError):
        logger.info('Version not found in server.json.')
        version = '0.0.0.0'
    # Split version into two floats.
    sv = version.split(".");
    v1 = 0;
    v2 = 0;
    if len(sv) == 1:
        v1 = int(v1[0])
    elif len(sv) > 1:
        v1 = float("%s.%s" % (sv[0],str(sv[1])))
        if len(sv) == 3:
            v2 = int(sv[2])
        else:
            v2 = float("%s.%s" % (sv[2],str(sv[3])))
    serverdata['version'] = version
    serverdata['version_major'] = v1
    serverdata['version_minor'] = v2
    return serverdata

# If we wanted to call this as a stand-alone script to generate the profile
# files, we'd do something like what's below but we'd need some way to 
# set the configuration.

if __name__ == "__main__":
    import logging,json
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=10,
        format='%(levelname)s:\t%(name)s\t%(message)s'
    )
    logger.setLevel(logging.DEBUG)

    # Test dictionaries to generate a custom nls file.
    app_map = {}

    # Only write the profile if the version is updated.
    sd = get_server_data(logger)
    if sd is not False:
        local_version = None
        try:
            with open(VERSION_FILE,'r') as vfile:
                local_version = vfile.readline()
                local_version = local_version.rstrip()
                vfile.close()
        except (FileNotFoundError):
            pass
        except (Exception) as err:
            logger.error('{0} failed to read local version from {1}: {2}'.format(pfx,VERSION_FILE,err), exc_info=True)

        if local_version == sd['profile_version']:
            #logger.info('{0} Not Generating new profile since local version {1} is the same current {2}'.format(pfx,local_version,sd['profile_version']))
            write_profile(logger, app_map)
        else:
            logger.info('{0} Generating new profile since local version {1} is not current {2}'.format(pfx,local_version,sd['profile_version']))
            write_profile(logger, app_map)
