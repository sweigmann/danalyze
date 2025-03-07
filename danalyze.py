# This is danalyze for differential image analysis.
#   (C) Sebastian Weigmann, 2025
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

import argparse
import os
import threading
import hashlib
import ssdeep

progname    = "danalyze"
progver     = 0.1


def hash_files(dir_prefix = '', dict = {}):
    if os.path.exists(dir_prefix):
        for root, dirs, files in os.walk(dir_prefix, topdown=True, followlinks=False):
            for file in files:
                fpath = os.path.join(root, file)
                common_prefix = os.path.commonprefix([dir_prefix, fpath])
                relative_fpath = os.path.relpath(fpath, common_prefix)
                with open(fpath, "rb") as f:
                    digest = hashlib.file_digest(f, "sha256")
                dict[relative_fpath] = {'size'  :   str(os.path.getsize(fpath)),
                                        'sha256':   digest.hexdigest(),
                                        'ssdeep':   ssdeep.hash_from_file(fpath)
                                        }
    return



def main():
    parser = argparse.ArgumentParser(prog = progname,
                                     description = "Recursive differential analysis on files")
    parser.add_argument("dir1", nargs=1)
    parser.add_argument("dir2", nargs=1)
    parser.add_argument('--version', action='version', version='%(prog)s v' + str(progver))
    args = parser.parse_args()
    dir1_prefix = args.dir1[0]
    dir2_prefix = args.dir2[0]
    dict1 = {}
    dict2 = {}
    thread1 = threading.Thread(target=hash_files, args=(dir1_prefix, dict1))
    thread2 = threading.Thread(target=hash_files, args=(dir2_prefix, dict2))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    # walk through both dicts
    # start with dict1 and seek all matches in dict2.
    # if there is no match, create a single-sided entry.
    result = {}
    dict1_keys = []
    dict1_keys.extend(dict1.keys())
    for f1 in dict1_keys:
        d1 = dict1.pop(f1)
        if f1 in dict2.keys():
            d2 = dict2.pop(f1)
            result[f1] = {
                'file1_size'  :   d1.get('size'),
                'file2_size'  :   d2.get('size'),
                'file1_sha256':   d1.get('sha256'),
                'file2_sha256':   d2.get('sha256'),
                'file1_ssdeep':   d1.get('ssdeep'),
                'file2_ssdeep':   d2.get('ssdeep'),
                'ssdeep_score':   str(ssdeep.compare(d1.get('ssdeep'), d2.get('ssdeep')))
            }
        else:
            result[f1] = {
                'file1_size'  :   d1.get('size'),
                'file2_size'  :   '',
                'file1_sha256':   d1.get('sha256'),
                'file2_sha256':   '',
                'file1_ssdeep':   d1.get('ssdeep'),
                'file2_ssdeep':   '',
                'ssdeep_score':   ''
            }
    assert(len(dict1) == 0)
    # if there are entries left in dict2...
    # create single-sided entries, as dict1 is empty.
    if len(dict2) > 0:
        dict2_keys = []
        dict2_keys.extend(dict2.keys())
        for f2 in dict2_keys:
            d2 = dict2.pop(f2)
            result[f2] = {
                'file1_size'  :   '',
                'file2_size'  :   d2.get('size'),
                'file1_sha256':   '',
                'file2_sha256':   d2.get('sha256'),
                'file1_ssdeep':   '',
                'file2_ssdeep':   d2.get('ssdeep'),
                'ssdeep_score':   ''
            }
    assert(len(dict2) == 0)
    # print out a sorted CSV...
    # print header
    print("filepath,file1_size,file2_size,file1_sha256,file2_sha256,file1_ssdeep,file2_ssdeep,ssdeep_score")
    # print body
    for f in sorted(result.keys()):
        print(
            '"' + f + '",' +
            result.get(f).get('file1_size') + ',' +
            result.get(f).get('file2_size') + ',' +
            result.get(f).get('file1_sha256') + ',' +
            result.get(f).get('file2_sha256') + ',' +
            result.get(f).get('file1_ssdeep') + ',' +
            result.get(f).get('file2_ssdeep') + ',' +
            result.get(f).get('ssdeep_score')
        )
    return


# void main() { do stuff }
if __name__ == '__main__':
    main()

