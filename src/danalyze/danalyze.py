# This is danalyze for differential image analysis.
#   (C) Sebastian Weigmann, 2025
#   This software is released under:
#   GNU GENERAL PUBLIC LICENSE, Version 3
#   Please find the full text in LICENSE.
#
# danalyze will recursively compare files within two given directories.
# results will be printed as CSV using these headers:
#   pos header
#   1   filepath
#   2   file1_size
#   3   file2_size
#   4   file1_sha256
#   5   file2_sha256
#   6   file1_ssdeep
#   7   file2_ssdeep
#   8   ssdeep_score
#
# Exit codes:
#   0:  all good
#   1:  generic error
#   2:  argument parser error
#
#
# generic imports
import argparse
import sys
import os
import threading
import hashlib

# specific imports
from enum import IntEnum, StrEnum

# 3rd-party imports
import ssdeep
import ssdeeper

# global variables
progname = "danalyze"
progver = "0.4"
simalg = None
outfile = None
resfilter = None
verbosity = 0


# error levels
class ERRLVL(IntEnum):
    CRIT = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4
    INFNT = 100


# filter metric
class RESFILTER(StrEnum):
    NONE = "none"
    SIZE = "size"
    HASH = "hash"


# generic wrapper for print()
def printmsg(msg="", errlvl=ERRLVL.INFNT):
    global verbosity
    if verbosity >= errlvl:
        if errlvl == ERRLVL.CRIT:
            msg = "CRITICAL: " + msg
        elif errlvl == ERRLVL.ERROR:
            msg = "ERROR:    " + msg
        elif errlvl == ERRLVL.WARN:
            msg = "WARNING:  " + msg
        elif errlvl == ERRLVL.INFO:
            msg = "INFO:     " + msg
        elif errlvl == ERRLVL.DEBUG:
            msg = "DEBUG:    " + msg
        print(msg, file=sys.stderr)


# directory traversal and file hashing is done here.
# this function is run as threads.
def hash_files(dir_prefix="", dir_dict=None):
    global verbosity
    global simalg
    # define a buffer size of 32kb (2^15 bytes) for file reading operations
    bufsize = 2**15
    for root, dirs, files in os.walk(dir_prefix, topdown=True, followlinks=False):
        for file in files:
            fpath = os.path.join(root, file)
            # if we hit a link, omit it.
            if os.path.islink(fpath):
                printmsg("LinksNotSupportedError: '%s'" % fpath, ERRLVL.WARN)
                continue
            # if we hit anything that is not a real file, omit it.
            if not os.path.isfile(fpath):
                printmsg("NotAFileError: '%s'" % fpath, ERRLVL.WARN)
                continue
            # construct a filepath which only includes the hashed directory subtree.
            # this filepath would be expected to match on both sides, dir1 and dir2.
            # the relative filepath becomes the key value for the result dictionary.
            common_prefix = os.path.commonprefix([dir_prefix, fpath])
            relative_fpath = os.path.relpath(fpath, common_prefix)
            try:
                hasher_sha256 = hashlib.sha256()
                hasher_ssdeep = simalg.Hash()
                with open(fpath, "rb") as f:
                    chunk = f.read(bufsize)
                    while chunk:
                        hasher_sha256.update(chunk)
                        hasher_ssdeep.update(chunk)
                        chunk = f.read(bufsize)
                digest_sha256 = hasher_sha256.hexdigest()
                digest_ssdeep = hasher_ssdeep.digest()
                dir_dict[relative_fpath] = {
                    "size": str(os.path.getsize(fpath)),
                    "sha256": digest_sha256,
                    "ssdeep": digest_ssdeep,
                }
            except Exception as excpt:
                # we get here if a real file is not readable (i.e. permission denied).
                printmsg("%s: %s" % (type(excpt).__name__, excpt), ERRLVL.ERROR)
                continue


# pathname arg validator for argparse
def type_path(pathname):
    if os.path.isdir(os.path.abspath(pathname)):
        return pathname
    else:
        raise FileNotFoundError("'" + pathname + "'")


# filepathname arg validator for argparse
def type_file(fpathname):
    if os.path.exists(os.path.abspath(fpathname)):
        raise FileExistsError("'" + fpathname + "'")
    else:
        return fpathname


def main():
    global progname
    global progver
    global outfile
    global resfilter
    global simalg
    global verbosity
    parser = argparse.ArgumentParser(
        prog=progname,
        description="Recursive differential analysis on files",
        epilog="Directories are traversed, but only real files are supported \
            for evaluation. Non-file objects such as links and unreadable \
            files will be silently dismissed, unless verbosity level is \
            greater than zero.",
    )
    parser.add_argument("dir1", nargs=1, type=type_path)
    parser.add_argument("dir2", nargs=1, type=type_path)
    parser.add_argument(
        "--filter",
        "-f",
        choices=[RESFILTER.NONE, RESFILTER.SIZE, RESFILTER.HASH],
        default=RESFILTER.NONE,
        help="Omit files from results. "
        + RESFILTER.NONE
        + ": nothing is omitted (default). "
        + RESFILTER.SIZE
        + ": files having the same size but may differ in content will be omitted. "
        + RESFILTER.HASH
        + ": files having the same sha256 hash will be omitted.",
    )
    parser.add_argument(
        "--simalg",
        "-s",
        choices=["ssdeep", "ssdeeper"],
        default="ssdeep",
        help="Select fuzzy hashing algorithm: original ssdeep (default) or ssdeeper",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=type_file,
        metavar="FILE",
        default=None,
        help="write results to FILE instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="can be given multiple times to increase verbosity",
    )
    parser.add_argument("--version", action="version", version="%(prog)s v" + progver)
    try:
        args = parser.parse_args()
        # make sure we didn't mess up the code. 
        # filter metric MUST be defined. fail otherwise.
        assert args.filter is not None
        # simalg algo MUST have been selected. fail otherwise.
        assert args.simalg is not None
    except Exception as excpt:
        # we get here when anything is wrong with provided arguments. fail and exit.
        printmsg("%s: %s" % (type(excpt).__name__, excpt), ERRLVL.CRIT)
        sys.exit(2)
    dir1_prefix = args.dir1[0]
    dir2_prefix = args.dir2[0]
    resfilter = args.filter
    if args.simalg == "ssdeep":
        simalg = ssdeep
    elif args.simalg == "ssdeeper":
        simalg = ssdeeper
    else:
        simalg = None
    # simalg algo MUST have been selected. fail otherwise.
    assert(simalg is not None)
    verbosity = args.verbose
    try:
        outfile = open(args.outfile, "w") if args.outfile else None
    except Exception as excpt:
        # no write permissions in the target directory? fail end exit!
        printmsg("%s: %s" % (type(excpt).__name__, excpt), ERRLVL.CRIT)
        sys.exit(2)
    printmsg("Creating threads...", ERRLVL.DEBUG)
    # two threads are spawned, one for each directory subtree. this allows for parallel
    # thread execution on hyperthreading architectures. it allows as well for distributed
    # reads from storage, if dir1 and dir2 subtrees live on different hardware storages.
    # otherwise, you will get concurrent IOPS, but exactly two. implicit tread safety is
    # guaranteed as number of threads is fixed and they each use distinct data structures.
    # thus, no blocking sync overhead is needed (i.e. mutexes, locking, conditions, ...).
    dict1 = {}
    dict2 = {}
    thread1 = threading.Thread(target=hash_files, args=(dir1_prefix, dict1))
    thread2 = threading.Thread(target=hash_files, args=(dir2_prefix, dict2))
    printmsg("Starting threads...", ERRLVL.DEBUG)
    thread1.start()
    thread2.start()
    printmsg("Traversing dictionaries and hashing files...", ERRLVL.INFO)
    thread1.join()
    thread2.join()
    printmsg("Threads have joined.", ERRLVL.DEBUG)
    # walk through both dicts.
    # this doesn't use any extra RAM, as entries-to-be-merged are popped from each dict.
    # start with dict1 and seek all matches in dict2.
    # if there is no match, create a single-sided entry.
    result = {}
    dict1_keys = []
    dict1_keys.extend(dict1.keys())
    printmsg("Merging results...", ERRLVL.INFO)
    printmsg(
        "Looking for files from '%s' in '%s'..." % (dir1_prefix, dir2_prefix),
        ERRLVL.DEBUG,
    )
    for f1 in dict1_keys:
        d1 = dict1.pop(f1)
        if f1 in dict2.keys():
            d2 = dict2.pop(f1)
            # apply filter...
            # hash:
            if (resfilter == RESFILTER.HASH) and (d1.get("sha256") == d2.get("sha256")):
                continue
            # size:
            elif (resfilter == RESFILTER.SIZE) and (d1.get("size") == d2.get("size")):
                continue
            # none:
            else:
                result[f1] = {
                    "file1_size": d1.get("size"),
                    "file2_size": d2.get("size"),
                    "file1_sha256": d1.get("sha256"),
                    "file2_sha256": d2.get("sha256"),
                    "file1_ssdeep": d1.get("ssdeep"),
                    "file2_ssdeep": d2.get("ssdeep"),
                    "ssdeep_score": str(
                        simalg.compare(d1.get("ssdeep"), d2.get("ssdeep"))
                    ),
                }
        else:
            result[f1] = {
                "file1_size": d1.get("size"),
                "file2_size": "",
                "file1_sha256": d1.get("sha256"),
                "file2_sha256": "",
                "file1_ssdeep": d1.get("ssdeep"),
                "file2_ssdeep": "",
                "ssdeep_score": "",
            }
    # make sure we didn't mess up the code. dict1 MUST be empty now. fail otherwise.
    assert len(dict1) == 0
    # if there are entries left in dict2, create single-sided entries, as dict1 is empty.
    # yes, absolutely!
    if len(dict2) > 0:
        printmsg("Collecting files left from '%s'..." % dir2_prefix, ERRLVL.DEBUG)
        dict2_keys = []
        dict2_keys.extend(dict2.keys())
        for f2 in dict2_keys:
            d2 = dict2.pop(f2)
            result[f2] = {
                "file1_size": "",
                "file2_size": d2.get("size"),
                "file1_sha256": "",
                "file2_sha256": d2.get("sha256"),
                "file1_ssdeep": "",
                "file2_ssdeep": d2.get("ssdeep"),
                "ssdeep_score": "",
            }
    else:
        printmsg("No files left in '%s'." % dir2_prefix, ERRLVL.DEBUG)
    # make sure we didn't mess up the code. dict2 MUST be empty now. fail otherwise.
    assert len(dict2) == 0
    # all files hashed, proceed with merging results.
    printmsg("Sorting results...", ERRLVL.INFO)
    result_keys_sorted = sorted(result.keys())
    # print out a sorted CSV...
    # print CSV header.
    if outfile:
        printmsg("Writing output to '%s'..." % args.outfile, ERRLVL.INFO)
    outfile_header = ",".join(
        [
            "filepath",
            "file1_size",
            "file2_size",
            "file1_sha256",
            "file2_sha256",
            "file1_" + simalg.__name__,
            "file2_" + simalg.__name__,
            simalg.__name__ + "_score",
        ]
    )
    if outfile:
        outfile.write(outfile_header + "\n")
    else:
        print(outfile_header)
    # print CSV body.
    for f in result_keys_sorted:
        outfile_line = ",".join(
            [
                '"'.join(["", f, ""]),
                result.get(f).get("file1_size"),
                result.get(f).get("file2_size"),
                result.get(f).get("file1_sha256"),
                result.get(f).get("file2_sha256"),
                result.get(f).get("file1_ssdeep"),
                result.get(f).get("file2_ssdeep"),
                result.get(f).get("ssdeep_score"),
            ]
        )
        if outfile:
            outfile.write(outfile_line + "\n")
        else:
            print(outfile_line)
    if outfile:
        outfile.close()
    return


# void main() { do stuff }
if __name__ == "__main__":
    try:
        main()
    except Exception as main_excpt:
        # yeah, this is truly unexpected. ever got CTRL+C'ed?? bail the heck out!
        printmsg("%s: %s" % (type(main_excpt).__name__, main_excpt), ERRLVL.CRIT)
        if outfile:
            outfile.close()
        sys.exit(1)
    sys.exit(0)
