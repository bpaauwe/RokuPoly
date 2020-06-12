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

def write_nls(logger, roku_list):
    sd = get_server_data(logger)
    if sd is False:
        logger.error("Unable to complete without server data...")
        return False

    logger.info("{0} Writing profile/nls/en_us.txt".format(pfx))
    if not os.path.exists("profile/nls"):
        try:
            os.makedirs("profile/nls")
        except:
            logger.error('unable to create node NLS directory.')

    try:
        nls = open("profile/nls/en_us.txt", "w")

        # Write out the standard node, command, and status entries

        nls.write("# controller\n")
        nls.write("ND-Roku-NAME = Roku Media Player\n")
        nls.write("ND-Roku-ICON = Output\n")
        nls.write("ST-ctl-ST-NAME = NodeServer Online\n")
        nls.write("ST-ctl-GV0-NAME = Log Level\n")
        nls.write("ST-ctl-GV1-NAME = Active Application Name\n")
        nls.write("ST-ctl-GV2-NAME = Active Application ID\n")
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
        nls.write("CMD-ctl-LAUNCH-NAME = Launch\n")
        nls.write("CMD-ctl-DISCOVER-NAME = Re-Discover\n")
        nls.write("CMD-ctl-REMOVE_NOTICES_ALL-NAME = Remove Notices\n")
        nls.write("CMD-ctl-UPDATE_PROFILE-NAME = Update Profile\n")
        nls.write("CMD-ctl-DEBUG-NAME = Log Level\n")
        nls.write("\n")

        for rk in roku_list:
            node_id = roku_list[rk]['node_id']
            nls.write("ND-" + node_id + "-NAME = " + rk + "\n")
            nls.write("ND-" + node_id + "-ICON = Output\n")
            for app in roku_list[rk]['apps']:
                logger.error(roku_list[rk]['apps'][app])
                (name, cnt) = roku_list[rk]['apps'][app]
                nls.write("%s-%d = %s\n" %(node_id, cnt, name))
            nls.write("\n")

        nls.write("DBG-0 = Off\n")
        nls.write("DBG-10 = Debug\n")
        nls.write("DBG-20 = Info\n")
        nls.write("DBG-30 = Warning\n")
        nls.write("DBG-40 = Error\n")
        nls.write("DBG-50 = Critical\n")

        nls.close()
    except:
        logger.error('Failed to write node NLS file.')
        nls.close()

    # Update the profile version file with the info from server.json
    with open(VERSION_FILE, 'w') as outfile:
        outfile.write(sd['profile_version'])
    outfile.close()

    # Create the zip file that can be uploaded to the ISY
    #write_profile_zip(logger)

    logger.info(pfx + " done.")


NODEDEF_TMPL = "  <nodeDef id=\"%s\" nodeType=\"139\" nls=\"%s\">\n"
STATUS_TMPL = "      <st id=\"%s\" editor=\"_25_0_R_0_%d_N_%s\" />\n"
LAUNCH_TMPL = "          <p id=\"\" editor=\"_25_0_R_0_%d_N_%s\" init=\"%s\" />\n"
def write_nodedef(logger, roku_list):
    sd = get_server_data(logger)
    if sd is False:
        logger.error("Unable to complete without server data...")
        return False

    nodedef = open("profile/nodedef/nodedefs.xml", "w")

    # First, write the controller node definition
    nodedef.write("<nodeDefs>\n")
    nodedef.write(NODEDEF_TMPL % ('Roku', 'ctl'))
    nodedef.write("    <sts>\n")
    nodedef.write("      <st id=\"ST\" editor=\"bool\" />\n")
    nodedef.write("      <st id=\"GV0\" editor=\"DEBUG\" />\n")
    nodedef.write("    </sts>\n")
    nodedef.write("    <cmds>\n")
    nodedef.write("      <sends />\n")
    nodedef.write("      <accepts>\n")
    nodedef.write("        <cmd id=\"DISCOVER\" />\n")
    nodedef.write("        <cmd id=\"REMOVE_NOTICES_ALL\" />\n")
    nodedef.write("        <cmd id=\"UPDATE_PROFILE\" />\n")
    nodedef.write("        <cmd id=\"DEBUG\">\n")
    nodedef.write("          <p id=\"\" editor=\"DEBUG\" init=\"GV0\" />\n")
    nodedef.write("        </cmd>\n")
    nodedef.write("      </accepts>\n")
    nodedef.write("    </cmds>\n")
    nodedef.write("  </nodeDef>\n\n")

    # Loop through and write the node defs for each device
    for rk in roku_list:
        logger.error(roku_list)
        no_apps = len(roku_list[rk]['apps'])
        node_id = roku_list[rk]['node_id']

        nodedef.write(NODEDEF_TMPL % (node_id, 'ctl'))
        nodedef.write("    <sts>\n")
        nodedef.write("      <st id=\"GV1\" editor=\"_25_0_R_0_%d_N_%s\" />\n" % (no_apps, node_id))
        nodedef.write("      <st id=\"GV2\" editor=\"app_id\" />\n")
        nodedef.write("    </sts>\n")
        nodedef.write("    <cmds>\n")
        nodedef.write("      <sends />\n")
        nodedef.write("      <accepts>\n")
        nodedef.write("        <cmd id=\"HOME\" />\n")
        nodedef.write("        <cmd id=\"REV\" />\n")
        nodedef.write("        <cmd id=\"FWD\" />\n")
        nodedef.write("        <cmd id=\"PLAY\" />\n")
        nodedef.write("        <cmd id=\"SELECT\" />\n")
        nodedef.write("        <cmd id=\"LEFT\" />\n")
        nodedef.write("        <cmd id=\"RIGHT\" />\n")
        nodedef.write("        <cmd id=\"DOWN\" />\n")
        nodedef.write("        <cmd id=\"UP\" />\n")
        nodedef.write("        <cmd id=\"BACK\" />\n")
        nodedef.write("        <cmd id=\"REPLAY\" />\n")
        nodedef.write("        <cmd id=\"INFO\" />\n")
        nodedef.write("        <cmd id=\"BACKSPACE\" />\n")
        nodedef.write("        <cmd id=\"SEARCH\" />\n")
        nodedef.write("        <cmd id=\"ENTER\" />\n")
        nodedef.write("        <cmd id=\"LAUNCH\">\n")
        nodedef.write(LAUNCH_TMPL % (no_apps, node_id, 'GV1'))
        nodedef.write("        </cmd>\n")
        nodedef.write("      </accepts>\n")
        nodedef.write("    </cmds>\n")
        nodedef.write("  </nodeDef>\n\n")

    nodedef.write("</nodeDefs>\n")

    nodedef.close()

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
