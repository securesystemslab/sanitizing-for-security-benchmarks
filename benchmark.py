import argparse
import os
import dangsan
import lowfat
import hextype
import hexvasan
import clang
import typesan
import valgrind


tools = [dangsan, lowfat, hextype, hexvasan, clang.asan, clang.msan,
         clang.ubsan, clang.cfi.all, clang.cfi.cast,
         clang.cfi.fwdedge, typesan, valgrind.memcheck]


def add_arguments(parser):
    subparsers = parser.add_subparsers(dest='command')

    for tool in tools:
        subparser = subparsers.add_parser(tool.command)
        subparser.add_argument('--setup', type=str, choices=tool.configs)
        subparser.add_argument('--test', type=str, choices=tool.configs)
        subparser.add_argument('--run', type=str, choices=tool.configs)
        subparser.add_argument('--clean', type=str, choices=tool.configs)


def parse_arguments(args):
    tool = next(tool for tool in tools if tool.command == args.command)
    if tool:
        if args.setup:
            config = args.setup
            workdir = '-'.join([args.command, config])
            if not os.path.exists(workdir):
                os.mkdir(workdir)
            os.chdir(workdir)
            tool.setup(config)
        elif args.test:
            config = args.test
            workdir = '-'.join([args.command, config])
            os.chdir(workdir)
            tool.test(config)
        elif args.run:
            config = args.run
            workdir = '-'.join([args.command, config])
            os.chdir(workdir)
            tool.run(config)
        elif args.clean:
            if raw_input('are you sure? (y/n)') == 'y':
                tool.clean(args.clean)


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    parse_arguments(args)


if __name__ == '__main__':
    main()
