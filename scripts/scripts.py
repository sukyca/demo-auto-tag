import sys
import pytz
import datetime as dt

import config
from flyway.make_flyway import make_flyway
from flyway.run_flyway import run_flyway

logger = config.get_logger(__file__)
DEPLOYMENT_DTTM_UTC = dt.datetime.now(pytz.UTC)

def validate_args(args):
    from flyway.validate import InvalidArgument
    
    if len(args) != 1:
        raise InvalidArgument('Expected one argument, got {}'.format(len(args)))
    arg = args[0]
    accepted_args = ('--make', '--validate', '--migrate')
    if arg not in accepted_args:
        raise InvalidArgument('Expected one of {}, got {}'.format(accepted_args, arg))
    return arg.replace('--', '')


if __name__ == '__main__':
    sys.argv.pop(0)
    arg = validate_args(sys.argv)
    
    logger.info("Flyway Deployment started at {}".format(DEPLOYMENT_DTTM_UTC))
    if arg == 'make':
        make_flyway()
    else:
        run_flyway(arg, DEPLOYMENT_DTTM_UTC)