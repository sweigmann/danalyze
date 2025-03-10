# danalyze

**danalyze - recursive differential analysis on files**

Given two directories, `danalyze` recursively analyzes all files
(and only real files) within them and computes sizes, `sha256` and 
`ssdeep` hashes. The CSV formatted results are dumped to the console.

Since `ssdeep` is about ten times slower than `sha256`, you may need 
some patience when scanning larger directory trees.

All runtime messages are written to `stderr`, while program output, 
the hashes, are written to `stdout` or to a file if specified.


## installation:

```bash
sudo apt install libfuzzy-dev
pipx install git+https://codeberg.org/DFIR/danalyze.git
```


## usage:

```bash
usage: danalyze [-h] [--filter {none,size,hash}] [--outfile FILE] [--verbose] [--version] dir1 dir2

Recursive differential analysis on files

positional arguments:
  dir1
  dir2

options:
  -h, --help            show this help message and exit
  --filter, -f {none,size,hash}
                        Omit files from results. 
                          none: nothing is omitted (default). 
                          size: files having the same size but may differ in content will be omitted. 
                          hash: files having the same sha256 hash will be omitted (implies same size).
  --outfile, -o FILE    write results to FILE instead of stdout
  --verbose, -v         can be given multiple times to increase verbosity
  --version             show program's version number and exit

Directories are traversed, but only real files are supported for evaluation. 
Non-file objects such as links and unreadable files will be silently dismissed, 
unless verbosity level is greater than zero.
```


## example:

```bash
danalyze -vv test/1/ test/2/
WARNING:  LinksNotSupportedError: 'test/1/deadlink'
WARNING:  LinksNotSupportedError: 'test/1/goodlink'
ERROR:    PermissionError: [Errno 13] Permission denied: 'test/2/notreadable'
```

### result:

```csv
filepath,file1_size,file2_size,file1_sha256,file2_sha256,file1_ssdeep,file2_ssdeep,ssdeep_score
"almost-same.bin",524288,524288,a7688ee8261ce5ff6921213f36f294d3902158191a12addb2a91f89a882b1492,0183a4bf1c2bec6d138c03d608736e96d24b7459247761db571fa9126cc8a33d,12288:C6zMvd21L9aQ9WgnRQyv0B7Fx/vc2jhwuNaRV9m4+I:C6zMvA1L9aQ9WgRUB7r3pwT9mDI,12288:C6zMvd21L9aQ9WgnRQyv0R7Fx/vc2jhwuNaRV9m4+I:C6zMvA1L9aQ9WgRUR7r3pwT9mDI,99
"almost-same.txt",708251,708251,62186454f4d509f32a3935080782b743f0626061ebf303c16d174333b3c45e8f,947ca345f8be1a06061a40c5162d93e7cb6c4136a6606149a021e2f6f22c7a5d,12288:oEl5uY+AomfFIJ3LbMNKOV63gdxLh70hkAB9x+ySmZGoTsR9hgXRIp:3Fom+JbbMgQdx+f+4bs3hgXu,12288:oEl5uY+AomfFIJ3LbMNKOV63gdxLh7FhkAB9x+ySmZGoTsR9hgXRIp:3Fom+JbbMgQdxPf+4bs3hgXu,99
"cicero.txt",1792,1819,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,77bb2c0d3092238e822dc16b6a7dbe72a51d99701e5289ad71da02dc28fc76c6,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,24:DGxpjKhOdoqE/2JnkZWevVPjNk/08WtqnNjUAHDe6gJWtf7VMvGbGiDs+lHV2zkc:ULWqrSPtG/DKThJAqvGbGIlHVakIm+,80
"different.txt",1792,2027,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,6f0cf13873ab282eaedd2d70bb705db7aab97879df9e10ae8f1afe48e4b451f6,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,24:DEPLi28PUOO7v20dvgBX5mtHNIYJVETYHVVTUWbrnFFmVVmKLruL9lirAb2T1SSL:p0ePzUNzWY1yWbCVVmKQN0oSiuNzbSeT,0
"one-side-has-more.txt",5873,6031,dbb197fdbeec8c5e2bf2d28b225ad61ab2c3674cdb8274445dcad2e4e9dc0e05,efb45b0f0349250fce48ba170812d82aa0fa4c51facb194f01d83f13d3caf300,96:B94TCU5AhUAFvA4qCemwfLR/UYcjsFj7n5qOLFlvDsbloNJerm0jAPGtq:fK0hU0oziGLRMIj7n5qOL/D8loNJbmjE,96:B94TCU5AhUAFvA4qCemwfLR/UYcjsFj7n5qOLFlvDsbloNJOrm0jAPGtq:fK0hU0oziGLRMIj7n5qOL/D8loNJrmjE,99
"only_1.txt",2308,,ffec38581fa1e5aeeffdc727c1d7e43360544b9d4ed6a4fa5360a9606f4be164,,48:sYr8tJBA8xh5hWJmu2Cc+sj+t017jWy/LpLYs:sYr8tJBjhyj8hN,,
"only_2.txt",,4868,,425cc93977a5ab45d68bfbbcf47db69890b5192415f681e93a5672239f06830b,,96:DHmBrBkIqMmnoCUtgfd5nyliuy/yJ6YzmnS+:jYrqI4noCUtGny7y/y4Yzm1,
"same-size.bin",4096,4096,3cfd9c381a29799fa867423a9bfd22c029abf97535fa92dd49c5509bda18d95c,87e250b1d97ca3e3f00f8a1a4496e0255d518f1452895966920683be9aa9894e,96:FHJkyXLTu5vR1ztP4Yu9SuRNzVIDRSMKZQ5LhL:dJ3S5vRPAREj9Ksl,96:VUKTMCz+q5itBZ23SDvBE11H6aav26HWHQfEIj4CcI/7:9TM85c0v15S2NrpI/7,0
"same-size.txt",5536,5536,dd32418c480cdc036419f628342bc0cd8907a30bc9d1c0daed728b7bf6a66ac4,43c99e8c43dd1045044dddfeb328dafe81773041fca17af0e8e016f7350e026a,96:bT8VFcxECv6t+fqXkT/GFk0hyBFdCQuuHjn+CSOUaWW9KPETf38/mULjORHkMFDI:bT1vq+yUOzIXHqCSOIWQIf8/jLjORHkT,96:okv91wNOinQY/h0dqEbn5RfKd91Xh/H9Frk/Q4JTK7BC4sft5O9r+lOCAdoP6O/G:lwNJnQY/Wbn5lKd91xojKHot5OV+gSLy,0
"same.txt",66716,66716,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,100
```

## testing:

You may use the test files contained in the `test/testfiles.txz` tarball. This set implements various test cases, such as:

* object is...
  - a link
  - not readable
  - present in only one subdirectory
* objects having the same filename...
  - are perfect copies of each other
  - completely differ from each other
  - share common content, but (at least) one side has some extra bytes
  - have the exact same size, but completely different content
  - have the exact same size, but differ in only one byte
