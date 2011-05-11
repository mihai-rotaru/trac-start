import os
from subprocess import call
from optparse import OptionParser
import ConfigParser

env_list = 'trac-environments'
env_list_str=''
auth_string=''

CONFIG_FILENAME = 'defaults.cfg'
config = ConfigParser.ConfigParser()
config.read( CONFIG_FILENAME )


# build the options
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option(  "-e", "--env-list",   
                    action  = "store", 
                    dest    = "env_list",
                    type    = "string",
                    help    = "a text file containing the absolute locations of trac environments ( one per row )",
                    default = env_list
                    )

parser.add_option(  "-a","--auth-string",
                    action  = "store",
                    dest    = "auth_string",
                    type    = "string", 
                    help    = "a string to pass to --basic-aut option",
                    default = config.get( "tracd","basic-auth" )
                    )

(options, args) = parser.parse_args()

# check options
if( options.env_list is not None ):
    if not os.path.isfile( options.env_list ):
        parser.error("Not a file: " + options.env_list)
if( options.auth_string is None ):
    parser.error("You must specify what to pass to the --basic-auth tracd option")

# construct the tracd command
f = open( options.env_list, 'r' )
for line in f:
    if( not line.startswith('#')):
        env_list_str += '"' + line.strip() + '" '

# run tracd
print ('tracd --port 8000 --basic-auth="' + options.auth_string + '" ' + env_list_str )

try:
    retcode =  call('tracd --port 8000 --basic-auth="' + options.auth_string + '" ' + env_list_str )
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    else:
        print >>sys.stderr, "Child returned", retcode
except OSError, e:
    print >>sys.stderr, "Execution failed:", e
except KeyboardInterrupt, e:
    print >>sys.stderr, "Keyboard interrupt", e
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise
