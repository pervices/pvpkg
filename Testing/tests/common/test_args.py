import argparse
import sys
from inspect import currentframe, getframeinfo
from . import log

class TestArgs:
    serial = None
    product = None
    channels = None
    report_dir = None
    docker_sha = None

    def __init__(self, parser=None, testDesc=""):
        if parser == None:
            parser = argparse.ArgumentParser(description = testDesc)
        parser.add_argument('-s', '--serial', required=True, default=None, help="Serial number of the unit")
        parser.add_argument('-p', '--product', required=True, help="Product, v for vaunt t for tate l for lily")
        parser.add_argument('-c', '--channels', required=False, type=int, nargs='+', default=[0,1,2,3], help="Channel list to use for testing. Example usage: [0,1,2,3]")
        parser.add_argument('-o', '--output', required=False, default=None, help="Report output directory")
        parser.add_argument('-d', '--docker', required=False, default=None, help="Docker SHA")
        args = parser.parse_args()
        
        self.serial = args.serial
        if len(args.channels) > 8 or len(args.channels) < 1:
            frameinfo = getframeinfo(currentframe())
            component = "{}:{}".format(frameinfo.filename, frameinfo.lineno)
            log.pvpkg_log_error(component, "Channels list must contain between 1 and 8 channels.")
            sys.exit(1)
        if len(args.channels) != len(set(args.channels)):
            frameinfo = getframeinfo(currentframe())
            component = "{}:{}".format(frameinfo.filename, frameinfo.lineno)
            log.pvpkg_log_error(component, "Channels list must contain unique elements.")
        else:
            self.channels = args.channels
        
        if args.product == 'v':
            self.product = "Vaunt"
        elif args.product == 't':
            self.product = "Tate"
        elif args.product == 'b':
            self.product = "BasebandTate"
        elif args.product == 'l':
            self.product = "Lily"
        else:
            log.pvpkg_log_error("TEST_ARGS", "Value of product argument must either be 'v' for vaunt, 't'for tate, 'b' for baseband tate, or 'l' for lily")
            sys.exit(1)

        self.report_dir = args.output
        self.docker_sha = args.docker
