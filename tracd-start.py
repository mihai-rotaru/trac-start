import os
import sys
from subprocess import call
from optparse import OptionParser
import ConfigParser

# returns true if the passed argument is a folder and contains
# a trac envrionment
def is_trac_env( folder ):
    if not os.path.isfile( folder + "/VERSION" ):
        return False
    else:
        f = open( folder + "/VERSION" )
        if not f.readline().startswith("Trac Environment"):
            return False
        else:
            return True

# set supported command line arguments
parser = OptionParser()
parser.add_option( "-e", "--env-list",     help = "a text file containing the absolute locations of trac environments ( one per line )")
parser.add_option(       "--python-path",  help = "absolute path to your Python folder ( Ex: C:\Python26 )")
parser.add_option( "-a", "--auth-string",  help = "a string to pass to --basic-aut option")
parser.add_option( "-p", "--port-number",  type = int, help    = "the port to run tracd on")
parser.add_option( "-s", "--service-name", help = "if supplied, run tracd as a service; string supplied is the name of the service. if this parameter is null, tracd will be started normally ( not as a service )")
parser.add_option(       "--nssm-path",    help    = "absolute path to nssm executable")
parser.add_option(       "--simulate",     action  = "store_true", help    = "don't actually run tracd, just show the generated command", default = False)

# check the config.cfg file
config = ConfigParser.ConfigParser()
config.read( sys.path[0] + "/config.cfg" )

# for each of the program's options, see if it's long name is specified in the cfg file
for opt in parser.option_list:
    optname = ""

    # get the long name of the option
    i = str( opt ).find( '/' )
    if i != -1:
        optname = str( opt )[i+1:]
    else:
        optname = str( opt )
    
    # remove the two leading dashes
    optname_nodashes = optname[2:]

    # look for this option in the config file
    try:
        optname_ = optname_nodashes.replace('-','_')
        parser.defaults[ optname_ ] = config.get( 'tracd', optname_nodashes )
    except ConfigParser.Error:
        pass

# parse command line arguments
(options, args) = parser.parse_args()

# check command line arguments
envs = ""
no_envs = 0
if( options.env_list is not None ):
    # is the path to env_list absoulte or relative
    if options.env_list.startswith ( '~' ):
        options.env_list = os.path.expanduser ( options.env_list )
    elif not os.path.isabs( options.env_list ):
        options.env_list = sys.path[0] + "/" + options.env_list
    
    # does the env_list file exist ?
    if not os.path.isfile( options.env_list ):
        parser.error("Not a file: " + options.env_list)
    else:
        # grab all the folders listed in the file, and check whether they are trac environments
        f = open( options.env_list )
        for line in f:
            line = line.strip()
            if not os.path.isdir( line ):
                print line + " is not a folder; skipping..."
            elif not is_trac_env( line ):
                print line + " is not a trac environment, skipping..."
            else:
                no_envs = no_envs + 1
                envs = envs + '"' + line + '" '
                
if no_envs == 0:
    print "FATAL ERROR: \"" + options.env_list + "\" does not contain any valid Trac environments; exiting..."
    sys.exit(1)

# start building the command to be exectuted
runme = ""
# run as a service ?
if( options.service_name is not None ):
    runme = '"' + options.nssm_path + '"' +\
            " " + "install" +\
            " " + options.service_name +\
            " " + '"' + options.python_path + r'\python.exe"' +\
            " " + '"' + options.python_path + r'\Scripts\tracd-script.py' + '"'
else:
    runme = "tracd"

# finish composing the command
runme = runme +\
        " " + "--port " + str(options.port_number) +\
        " " + "--basic-auth=" + options.auth_string +\
        " " + envs

print "command: " + runme

if options.simulate == 'False':
    try:
        retcode =  call( runme )
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
        elif retcode == 0:
            if( options.service_name is not None ):
                print 'net start ' + options.service_name
                call('net start ' + options.service_name)
        else:
            print >>sys.stderr, "Child returned", retcode
    except OSError, e:
        print >>sys.stderr, "Execution failed:", e
    except KeyboardInterrupt, e:
        print >>sys.stderr, "Keyboard interrupt", e
    except:
        print "Unexpected error:", sys.exc_info()[0]
