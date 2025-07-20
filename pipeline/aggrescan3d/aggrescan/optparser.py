# -*- coding: utf-8 -*-

"""Module that handles argument parsing and stores default program options"""
import argparse
from os import getcwd
from os.path import abspath, join, isfile
import json
import re
import logger
from pkg_resources import resource_filename


_name = "AggParser"

_shorts = {
    'i': 'protein',
    'm': 'mutate',
    'd': 'dynamic',
    'D': 'distance',
    'w': 'work_dir',
    'O': 'overwrite',
    'v': 'verbose',
    'C': 'chain',
    'f': 'foldx',
    'M': 'movie',
    'n': 'naccess',
    'o': 'output',
    'r': 'remote',
    'cabs': "cabs_dir",
    'cabs_config': 'cabs_config',
    'n_models': 'n_models',
    'am': 'auto_mutation',
    'ph': 'ph'
}


class ExtendAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


def ph_range(ph):
    try:
        ph_value = float(ph)
    except ValueError:
        raise argparse.ArgumentTypeError("pH should be provided as a non-zero number value")
    if ph_value <= 0 or ph_value > 14:
        raise argparse.ArgumentTypeError("pH should be take values between (0,14]")
    else:
        return ph_value


def parse(options):
    parser = get_parser_object()
    read = parser.parse_args(options)
    data, mut = [], []
    if read.config_file:
        data, mut = parse_config_file(read.config_file)
    data.extend(options)
    read = parser.parse_args(data)
    auto_mutation = _parse_auto_mut(read.auto_mutation)

    # This is a safety measure in case a path is changed inside the program and the relative would be no longer valid
    cabs_config, foldx, naccess = '', '', ''
    if read.cabs_config:
        cabs_config = abspath(read.cabs_config)
    if read.foldx != "argument_not_used" and read.foldx is not None:   # Prevent assiging a path to not-used argument
        read.foldx = abspath(read.foldx)
    if read.naccess:
        naccess = abspath(read.naccess)
    foldx = _handle_foldx(read.foldx)
    work_dir = abspath(read.work_dir)
    tmp_dir = join(work_dir, "tmp")
    new_mut = _parse_mut(read.mutate)
    if new_mut:
        mut.extend(new_mut)
    # Catch some of the unwanted option combinations here.
    if new_mut and auto_mutation:
        raise logger.InputError("Both manual and automated mutations selected. Please select just one of those as they are exclusive.")
    if auto_mutation and read.dynamic:
        raise logger.InputError("Automated mutations are not (yet?) supported with dynamic mode.")
    if auto_mutation and not foldx:
        raise logger.InputError("Automated mutations require FoldX to work. Please specify a path with -f.")

    options = {
        'protein': read.protein,
        'dynamic': read.dynamic,
        'mutate': mut,
        'distance': read.distance,
        'work_dir': work_dir,
        'overwrite': read.overwrite,
        'verbose': read.verbose,
        'chain': read.chain,
        'movie': read.movie,
        'naccess': naccess,
        "foldx": foldx,
        'auto_mutation': auto_mutation,
        'remote': read.remote,
        "cabs_dir": read.cabs_dir,
        "cabs_config": cabs_config,
        "n_models": read.n_models,
        "tmp_dir": tmp_dir,
        "subprocess": read.subprocess,
        "ph": read.ph
    }
    return options


def parse_config_file(filename):
    parsed = []
    option_pattern = re.compile(
        r'(?P<option>[^:=]*)'
        r'[:=]'
        r'(?P<value>.*)$'
    )
    mutation_pattern = re.compile(r'{+.+\}+')
    path = abspath(filename)
    logger.debug(module_name=_name, msg="Parsing data from: %s" % path)
    to_mutate = []
    try:
        with open(path, 'r') as f:
            for line in f:
                if line == '' or line[0] in ';#\n':
                    continue
                elif mutation_pattern.search(line):
                    try:
                        mutation = mutation_pattern.findall(line)[0]
                        mutation = re.sub("\'", "\"", mutation)
                        to_mutate.append(json.loads(mutation))
                    except Exception:
                        logger.critical(module_name=_name,
                                        msg="Error while loading the mutation table in line:\n %s" % line.strip("\n"))
                        raise logger.InputError("Failed to properly load config file. Quitting.")
                elif line.startswith("am") or line.startswith("auto_mutation"): # Special case, this is getting super messy
                    parsed.append("--auto_mutation")
                    parsed.append(" ".join(line.split()[1:]))
                else:
                    match = option_pattern.match(line)
                    if match:
                        option, value = match.groups()
                        option = option.strip()
                        if option in _shorts.values():
                            if value.strip() != "True":
                                parsed.append("--"+option)
                                parsed.append(value.strip())
                            else:
                                parsed.append("--"+option)
                        elif option in _shorts.keys():
                            if value.strip() != "True":
                                parsed.append("-"+option)
                                parsed.append(value.strip())
                            else:
                                parsed.append("-"+option)

                        else:
                            logger.warning(module_name=_name,
                                           msg="option: %s seen in config file not recognized" % option)
                    elif line.strip() in _shorts.values():
                        parsed.append("--"+line.strip())
                    elif line.strip() in _shorts.keys():
                        parsed.append("-"+line.strip())
                    else:
                        logger.warning(module_name=_name, msg="line: %s couldn't be parsed" % line.strip("\n"))

    except IOError:
        raise logger.InputError("Could not load the file %s" % path)
    return parsed, to_mutate


def save_config_file(config, work_dir):
    tmp = ""
    for argName, argValue in config.items():
        if type(argValue) == list:      # This will catch mutations
            for mutation in argValue:
                tmp += json.dumps(mutation) + "\n"  # assuming its a mutation entry, which should be dumps'able
        elif type(argValue) == tuple:   # This will catch automated mutations, as long as no new tuples/lists are introduced this works
            if len(argValue) > 2:
                tmp += "%s: %d %d %s\n" % (argName, argValue[0], argValue[1], " ".join([i['idx']+i['chain'] for i in argValue[2]]))
            else:
                tmp += "%s: %d %d\n" % (argName, argValue[0], argValue[1])
        elif argValue and (argName in _shorts.keys() or argName in _shorts.values()):
            tmp += "%s : %s\n" % (argName, argValue)

    logger.to_file(filename=join(work_dir, "config.ini"), content=tmp)


def get_parser_object():
    parser = argparse.ArgumentParser(
        description='Aggrescan 3D standalone application. Please read and run configReadme.ini to test if the program works.')
    parser.register('action', 'extend', ExtendAction)

    parser.add_argument('-c',
                        '--config_file',
                        metavar='',
                        type=str,
                        help='''Input file with specified config options. One can specify a config file and some additional flags
                             Command line options have priority over config file. 
                             For further help on creating config files please refer to configReadme.ini''')

    parser.add_argument('-i',
                        '--protein',
                        metavar='',
                        type=str,
                        help='Input pdb code or a path to file on which the simulation is performed')

    parser.add_argument('-d',
                        '--dynamic',
                        default=False,
                        action='store_true',
                        help='Use the dynamic module for the simulation. '
                             'CABS flex will be used to perform a protein dynamics simulation '
                             'If CABS is not installed but present in the filesystem use --cabs_dir to provide a path to its location '
                             '--cabs_config can be used to provide a CABS config file '
                             '--n_models can be used to decide how many models will be taken into further calculations')

    parser.add_argument('-m',
                        '--mutate',
                        metavar='',
                        default='',
                        type=str,
                        nargs='+',
                        action='extend',
                        help="""Provide a residue mutation. This option can be used multiple times to provide multiple mutations.
                                 The format is: <Old residue><New residue><Residue number><Chain ID> 
                                 For example: MW1A to change the first residue of chain A from methionine to tyrosine.
                                 Please note that this option requires FoldX usage.""")

    parser.add_argument('-D',
                        '--distance',
                        metavar='',
                        default=10,
                        type=int,
                        help='Distance cutoff for naccess calculations. Default: 10')

    parser.add_argument('-w',
                        '--work_dir',
                        metavar='',
                        default=getcwd(),
                        type=str,
                        help="Sets the directory in which the simulation is performed")

    parser.add_argument('--cabs_dir',
                        metavar='',
                        default='',
                        type=str,
                        help="If used CABS will be run from the provided directory. Should be used when CABS is not installed"
                             "or one wants to use a specific CABS version for the dynamic simulations")

    parser.add_argument('--cabs_config',
                        metavar='',
                        default='',
                        type=str,
                        help="If used CABS will be run with selected config file. "
                             "Aggrescan will not parse the config in any way so its up to the user to supply a working config file."
                             "For debugging purposes use verboisty 3 or higher, "
                             "CABS simulation log will be then kept, see the CABSlog file for details on what went wrong with the CABS run."
                             "Few caveats include:"
                             "CABS work-dir should not be used"
                             "if --n_models is used it will overwrite --clustering-medoids in the config file specified by this option"
                             "CABS input option will be overwritten"
                             "--aa-rebuild and --remote will be specified by default")

    parser.add_argument('--n_models',
                        metavar='',
                        default=12,
                        type=int,
                        help='Sets the number of models CABS will generate in the dynamic analysis.'
                             'This option will overwrite cabs config file if you chose both options'
                             ' '
                        )

    parser.add_argument('-r',
                        '--remote',
                        default=False,
                        action="store_true",
                        help='Automatically redirects output to a Aggrescan.log file created in the working directory,'
                             'turns off log coloring. Piping standard error will not work with this option.'
                             'If a log file already exists it will be appended to.')

    parser.add_argument('-O',
                        '--overwrite',
                        default=False,
                        action='store_true',
                        help="""If the working directory already exists and contains an output.pdb file 
                         this will stop the program to prevent overwriting possible results that might be there""")

    parser.add_argument('-f',
                        '--foldx',
                        metavar='',
                        type=str,
                        nargs='?',
                        default="argument_not_used",
                        help="""The program will attempt to run foldX on the provided pdb file or code 
                                 using the path provided in this option. Once the path is provided subsequent runs can 
                                 can omit the path and simply use -f (it will be written in program data""")

    parser.add_argument('-v',
                        '--verbose',
                        metavar='',
                        default=2,
                        type=int,
                        help="""Sets the verbosity of the program 
                                 0 for silent mode (only critical messages) and 4 for maximum verbosity. 
                                 Verbosity level 3 might raise some Exceptions that would otherwise only be logged as critical messages""")

    parser.add_argument('-C',
                        '--chain',
                        metavar='',
                        default='',
                        type=str,
                        help="""Only consider a specific chain while performing calculations""")

    parser.add_argument('-M',
                        '--movie',
                        metavar='',
                        default='',
                        type=str,
                        help="""Create a short movie of the result protein. Available formats: mp4, webm
                                 Usage: -m mp4
                                 Please note pymol and avconv are used and need to be installed for this option to work""")
    parser.add_argument('-n',
                        '--naccess',
                        metavar="",
                        default="",
                        type=str,
                        help="""Run the simulation with naccess instead of freeSasa. 
                                Run this argument with a path to the naccess program exectuable.""")

    parser.add_argument('-am',
                        '--auto_mutation',
                        metavar='',
                        default='is_not_used',  # The actual option is in _parse_auto_mut, this is to recognize the argument was NOT used
                        nargs='?',
                        type=str,
                        help="Automatically mutate most aggregation prone residues The option should be formatted as follows: "
                             "number_of mutations number_of_used_processes [list of residues that are not to be mutated]"
                             " The list is optional and if no arguments are specified two resides using two threads will be attempted"
                              "The list should follow the naming convention of <Residue number><Chain ID>" 
                              "For example: '2 2 1A' to mutate 2 residues using 2 processes at once and exclude the first residue of A chain"
                              " from the mutation candidates. Which will result in 8 mutants (4*2)")

    parser.add_argument('--subprocess',
                        default=False,
                        action="store_true",
                        help="""Internal option but can be used by the user - this is used to signal that the run is 
                                actually a subprocess of A3D's auto mutation procedure. Using this option means that no 
                                energy minimization will be perfomed before creating a mutant.""")

    parser.add_argument('--ph',
                        '-ph',
                        type=ph_range,
                        metavar="(0-14]",
                        help="""Use a different A3D scale that takes pH into account, which will change especially the values
                        for acidic/base aminoacids. See our wiki for a more detailed explanation""")

    return parser


def _parse_auto_mut(argument):
    _pattern = re.compile('(?P<id>[0-9]+)'
                          '(?P<chain>[A-Z])')

    if argument == "is_not_used":
        return None
    elif argument is None:  # Happens when option with no arguments is used
        return 2, 2
    else:
        argument = argument.strip()
        parsed_argument = argument.split()
        if parsed_argument[0] == ":" or parsed_argument[0] == "=":  # This can happen in a config file
            parsed_argument.pop(0)
        if len(parsed_argument) == 1:
            parsed_argument += "2"  # To add to the default
        try:
            n_mutations = int(parsed_argument[0])
        except ValueError:
            raise logger.InputError("Failed to convert the first argument for automated mutations to a number. Expected a number,"
                                    "got %s. Valid input would look like: -am '2 2 1A 2A'. Your input: %s" % (parsed_argument[0], argument))
        try:
            n_threads = int(parsed_argument[1])
        except ValueError:
            raise logger.InputError("Failed to convert the second argument for automated mutations to a number. Expected a number,"
                                    "got %s. Valid input would look like: -am '2 2 1A'. Your input: %s" % (parsed_argument[1], argument)
                                    )

        if len(parsed_argument) > 2:
            excluded_list = []
            for item in parsed_argument[2:]:
                try:
                    parse = _pattern.match(item).groups()
                    excluded_list.append({
                        'idx': parse[0],
                        'chain': parse[1]
                    })
                except AttributeError:
                    raise logger.InputError(
                        "Failed to parse excluded residues for aumated mutations. Residues should be provided  in a "
                        "<Residue ID><Chain> format i.e. 1A 2B etc. Failed item: %s. Whole input for the option: %s" % (item, argument))
            return n_mutations, n_threads, excluded_list
        else:
            return n_mutations, n_threads


def _parse_mut(mutation_list):
    p = re.compile('(?P<oldres>[A-Z])'
                   '(?P<newres>[A-Z])'
                   '(?P<id>[0-9]+)'
                   '(?P<chain>[A-Z])')
    out_list = []
    for mutation in mutation_list:
        try:
            parsed = p.match(mutation).groups()
            out_list.append({'oldres': parsed[0],
                             'newres': parsed[1],
                             'idx': parsed[2],
                             'chain': parsed[3]
                             })
        except AttributeError:
            raise logger.InputError(
                                "Your mutation %s was provided in wrong format. " % mutation +
                                "Correct formatting is <Oldres><Newres><ID><chain>. "
                                "For example MW1A. Mind the capital letters. ")
    return out_list


def _handle_foldx(user_input):
    """
    Either save the provdied FoldX path to a file or try to read the path from the file.
    If the user sepcified -f with no argument the user_input is None
    if the user never used the -f the user_input is default ("")
    """
    if user_input == "argument_not_used":    # The option was never selected
        return ""
    if user_input is not None:  # A path is actually provided
        try:
            with open(join(resource_filename("aggrescan", "data"), "foldx_dir.txt"), 'w') as f:
                f.write(user_input)
        except IOError as e:
            if "Permission denied" in str(e):
                try:
                    with open(join(resource_filename("aggrescan", "data"), "foldx_dir.txt"), 'r') as f:
                        user_input = f.read().strip()
                except IOError:
                    raise logger.InputError(
                        "--foldx option used but no path has been specified. If you've never used the option "
                        "you need to privde a path to FoldX directory. It can be ommited in subsequent runs "
                        "as it will be saved in program's data")
    else:
        if not isfile(join(resource_filename("aggrescan", "data"), "foldx_dir.txt")):
            raise logger.InputError("--foldx option used but no path has been specified. If you've never used the option "
                                    "you need to privde a path to FoldX directory. It can be ommited in subsequent runs "
                                    "as it will be saved in program's data")
        with open(join(resource_filename("aggrescan", "data"), "foldx_dir.txt"), 'r') as f:
            user_input = f.read().strip()
    return user_input
