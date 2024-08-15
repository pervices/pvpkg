import argparse
import sys

class TestArgs:
    serial = None
    product = None
    report_dir = None
    docker_sha = None

    def __init__(self, parser=None, testDesc=""):
        if parser == None:
            parser = argparse.ArgumentParser(description = testDesc)
        parser.add_argument('-s', '--serial', required=True, default=None, help="Serial number of the unit")
        parser.add_argument('-p', '--product', required=True, help="Product, v for vaunt t for tate l for lily")
        parser.add_argument('-o', '--output', required=False, default=None, help="Report output directory")
        parser.add_argument('-d', '--docker', required=False, default=None, help="Docker SHA")
        args = parser.parse_args()
        self.serial = args.serial
        if args.product == 'v':
            self.product = "Vaunt"
        elif args.product == 't':
            self.product = "Tate"
        elif args.product == 'l':
            self.product = "Lily"
        else:
            print("Value of product argument must either be 'v' for vaunt, 't' for tate, or 'l' for lily")
            sys.exit(1)

        self.report_dir = args.output
        self.docker_sha = args.docker
