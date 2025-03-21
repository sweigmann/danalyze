# danalyze

**danalyze - recursive differential analysis on files**

Given two directories, `danalyze` recursively analyzes all files
(and only real files) within them and computes sizes, `sha256` and
`ssdeep` or `ssdeeper` hashes.

The CSV formatted results are dumped to the console.

Since `ssdeep` is about ten times slower than `sha256`, you may need
some patience when scanning larger directory trees.

All runtime messages are written to `stderr`, while program output,
the hashes, are written to `stdout` or to a file if specified.

<img src="https://github.com/sweigmann/danalyze/actions/workflows/codeql-analysis.yml/badge.svg?branch=main">
<img src="https://github.com/sweigmann/danalyze/actions/workflows/python-linux.yml/badge.svg?branch=main">
<img src="https://github.com/sweigmann/danalyze/actions/workflows/debian.yml/badge.svg?branch=main">
<img src="https://github.com/sweigmann/danalyze/actions/workflows/ubuntu.yml/badge.svg?branch=main">

## `ssdeep` and `ssdeeper`:

The [`ssdeep`](https://github.com/ssdeep-project/ssdeep.git) project and [Python bindings](https://github.com/DinoTools/python-ssdeep.git) provide the original similarity hashing algorithm for `danalyze`.

The [`ssdeeper`](https://github.com/fkie-cad/ssdeeper.git) project by Fraunhofer FKIE introduced some improvements, from which the flavor `ssdeep-refactored-4b-djb2-nocommonsub` was selected. These augmentations have also been made available to `danalyze` as an alternative similarity hashing algorithm.


## installation:

```bash
sudo apt install libfuzzy-dev
pipx install git+https://codeberg.org/DFIR/danalyze.git
```


## usage:

```bash
usage: danalyze [-h] [--filter {none,size,hash}] [--simalg {ssdeep,ssdeeper}] [--outfile FILE] [--verbose] [--version] dir1 dir2

Recursive differential analysis on files

positional arguments:
  dir1
  dir2

options:
  -h, --help            show this help message and exit
  --filter, -f {none,size,hash}
                        Omit files from results. none: nothing is omitted (default). size: files having the same size but may differ in content will be omitted. hash: files having the same sha256 hash
                        will be omitted.
  --simalg, -s {ssdeep,ssdeeper}
                        Select fuzzy hashing algorithm: original ssdeep (default) or ssdeeper
  --outfile, -o FILE    write results to FILE instead of stdout
  --verbose, -v         can be given multiple times to increase verbosity
  --version             show program's version number and exit

Directories are traversed, but only real files are supported for evaluation. Non-file objects such as links and unreadable files will be silently dismissed, unless verbosity level is greater than zero.
```


## examples:

### using `ssdeep`:

```bash
danalyze -vv test/1/ test/2/
WARNING:  LinksNotSupportedError: 'test/1/deadlink'
WARNING:  LinksNotSupportedError: 'test/1/goodlink'
ERROR:    PermissionError: [Errno 13] Permission denied: 'test/2/notreadable'
```

#### result:

```csv
filepath,file1_size,file2_size,file1_sha256,file2_sha256,file1_ssdeep,file2_ssdeep,ssdeep_score
"almost-same.bin",524288,524288,0183a4bf1c2bec6d138c03d608736e96d24b7459247761db571fa9126cc8a33d,a7688ee8261ce5ff6921213f36f294d3902158191a12addb2a91f89a882b1492,12288:C6zMvd21L9aQ9WgnRQyv0R7Fx/vc2jhwuNaRV9m4+I:C6zMvA1L9aQ9WgRUR7r3pwT9mDI,12288:C6zMvd21L9aQ9WgnRQyv0B7Fx/vc2jhwuNaRV9m4+I:C6zMvA1L9aQ9WgRUB7r3pwT9mDI,99
"almost-same.txt",708251,708251,947ca345f8be1a06061a40c5162d93e7cb6c4136a6606149a021e2f6f22c7a5d,62186454f4d509f32a3935080782b743f0626061ebf303c16d174333b3c45e8f,12288:oEl5uY+AomfFIJ3LbMNKOV63gdxLh7FhkAB9x+ySmZGoTsR9hgXRIp:3Fom+JbbMgQdxPf+4bs3hgXu,12288:oEl5uY+AomfFIJ3LbMNKOV63gdxLh70hkAB9x+ySmZGoTsR9hgXRIp:3Fom+JbbMgQdx+f+4bs3hgXu,99
"cicero.txt",1819,1792,77bb2c0d3092238e822dc16b6a7dbe72a51d99701e5289ad71da02dc28fc76c6,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,24:DGxpjKhOdoqE/2JnkZWevVPjNk/08WtqnNjUAHDe6gJWtf7VMvGbGiDs+lHV2zkc:ULWqrSPtG/DKThJAqvGbGIlHVakIm+,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,80
"different.txt",2027,1792,6f0cf13873ab282eaedd2d70bb705db7aab97879df9e10ae8f1afe48e4b451f6,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,24:DEPLi28PUOO7v20dvgBX5mtHNIYJVETYHVVTUWbrnFFmVVmKLruL9lirAb2T1SSL:p0ePzUNzWY1yWbCVVmKQN0oSiuNzbSeT,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,0
"one-side-has-more.txt",6031,5873,efb45b0f0349250fce48ba170812d82aa0fa4c51facb194f01d83f13d3caf300,dbb197fdbeec8c5e2bf2d28b225ad61ab2c3674cdb8274445dcad2e4e9dc0e05,96:B94TCU5AhUAFvA4qCemwfLR/UYcjsFj7n5qOLFlvDsbloNJOrm0jAPGtq:fK0hU0oziGLRMIj7n5qOL/D8loNJrmjE,96:B94TCU5AhUAFvA4qCemwfLR/UYcjsFj7n5qOLFlvDsbloNJerm0jAPGtq:fK0hU0oziGLRMIj7n5qOL/D8loNJbmjE,99
"one-side-has-much-more.txt",8704,4096,2d61a3006ddec2d90f3418e159bc0872446b2529376c7d400fecd03246ee4925,f5bb9e447168d653c5f2c7b1bdfa5400626b5e0e99eea5789d754ba4ac2f0b0d,192:Afpwh2iOkbMfhNb3OalRQjxYM4ZmRMhX/2O0zpQcn41zyvs6LG:uwUhxfz3OrWZmRoX/2OxcnOeM,48:Az13jzXEOufqgJWcfaI3hgJqGc2fwxMeWCRIqWyCp7bcLb6nTRHCDVfTMjLnHJ3m:Az13Hcy/Jqdtx/WpbcQaLMjzhd7b/g,0
"only_1.txt",,2308,,ffec38581fa1e5aeeffdc727c1d7e43360544b9d4ed6a4fa5360a9606f4be164,,48:sYr8tJBA8xh5hWJmu2Cc+sj+t017jWy/LpLYs:sYr8tJBjhyj8hN,
"only_2.txt",4868,,425cc93977a5ab45d68bfbbcf47db69890b5192415f681e93a5672239f06830b,,96:DHmBrBkIqMmnoCUtgfd5nyliuy/yJ6YzmnS+:jYrqI4noCUtGny7y/y4Yzm1,,
"same-size.bin",4096,4096,87e250b1d97ca3e3f00f8a1a4496e0255d518f1452895966920683be9aa9894e,3cfd9c381a29799fa867423a9bfd22c029abf97535fa92dd49c5509bda18d95c,96:VUKTMCz+q5itBZ23SDvBE11H6aav26HWHQfEIj4CcI/7:9TM85c0v15S2NrpI/7,96:FHJkyXLTu5vR1ztP4Yu9SuRNzVIDRSMKZQ5LhL:dJ3S5vRPAREj9Ksl,0
"same-size.txt",5536,5536,43c99e8c43dd1045044dddfeb328dafe81773041fca17af0e8e016f7350e026a,dd32418c480cdc036419f628342bc0cd8907a30bc9d1c0daed728b7bf6a66ac4,96:okv91wNOinQY/h0dqEbn5RfKd91Xh/H9Frk/Q4JTK7BC4sft5O9r+lOCAdoP6O/G:lwNJnQY/Wbn5lKd91xojKHot5OV+gSLy,96:bT8VFcxECv6t+fqXkT/GFk0hyBFdCQuuHjn+CSOUaWW9KPETf38/mULjORHkMFDI:bT1vq+yUOzIXHqCSOIWQIf8/jLjORHkT,0
"same.txt",66716,66716,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,100
```

### using `ssdeeper`:

```bash
danalyze -vv -s ssdeeper test/1/ test/2/
WARNING:  LinksNotSupportedError: 'test/1/deadlink'
WARNING:  LinksNotSupportedError: 'test/1/goodlink'
ERROR:    PermissionError: [Errno 13] Permission denied: 'test/2/notreadable'
```

#### result:

```csv
filepath,file1_size,file2_size,file1_sha256,file2_sha256,file1_ssdeeper,file2_ssdeeper,ssdeeper_score
"almost-same.bin",524288,524288,0183a4bf1c2bec6d138c03d608736e96d24b7459247761db571fa9126cc8a33d,a7688ee8261ce5ff6921213f36f294d3902158191a12addb2a91f89a882b1492,12288:kxGQsYE8f0qofG9+dlB3jvVLaMtj5Vy6jvEC+Kqc:kUPK+Pdj0Kbt,12288:kxGQsYE8f0qofG9+dlB3jfVLaMtj5Vy6jvEC+Kqc:kUPK+PdjkKbt,98
"almost-same.txt",708251,708251,947ca345f8be1a06061a40c5162d93e7cb6c4136a6606149a021e2f6f22c7a5d,62186454f4d509f32a3935080782b743f0626061ebf303c16d174333b3c45e8f,12288:EKgdnBC86hf3RwNW1MD03sntIPiX8nUmbok2PGxKkKp/zRPZJYZP8+tDabcAtgmCXlw56M25uH:E+fd6IPVnFgkQ27CZAS,12288:EKgdnBC86hf3RwNW1MD03sntIPiX8nUmboD2PGxKkKp/zRPZJYZP8+tDabcAtgmCXlw56M25uH:E+fd6IPVIFgkQ27CZAS,100
"cicero.txt",1819,1792,77bb2c0d3092238e822dc16b6a7dbe72a51d99701e5289ad71da02dc28fc76c6,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,48:SgrCQDWWsH/RpwmV7Bw0DdMrz0so2lIsKUE5HC:5yBBgY4Uk,48:SWrCQDWWsHKOgpwwVXBw0DdMrz0so2CIsKRE5HC:TyMBgY4yk,82
"different.txt",2027,1792,6f0cf13873ab282eaedd2d70bb705db7aab97879df9e10ae8f1afe48e4b451f6,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,48:SzwIwh17MqoT3G/og+IB5QGjnWKJS6AN1gX+iR:zhfMPTRSx97,48:SWrCQDWWsHKOgpwwVXBw0DdMrz0so2CIsKRE5HC:TyMBgY4yk,22
"one-side-has-more.txt",6031,5873,efb45b0f0349250fce48ba170812d82aa0fa4c51facb194f01d83f13d3caf300,dbb197fdbeec8c5e2bf2d28b225ad61ab2c3674cdb8274445dcad2e4e9dc0e05,48:e6V8qq2I0T/uskNATME/byAo/kvvHiY7bQprPQR9eBRQtD+3QrYVs9t6Gj9UmFHCfCkoFjyShmfXwOEm1EH6E9Meu:VPlocC8bSLSYWy6j+h4ON1EH39Y,48:e6V8qq2I0T/uskNATME/byAo/kvvHiY7bQprPQR9eBRQtD+3QrYVs9t6Gj9UmFHCfCkoFjFhmfXwOEm1EH6E9Meu:VPlocC8bSLSYWy6j+hgON1EH39Y,99
"one-side-has-much-more.txt",8704,4096,2d61a3006ddec2d90f3418e159bc0872446b2529376c7d400fecd03246ee4925,f5bb9e447168d653c5f2c7b1bdfa5400626b5e0e99eea5789d754ba4ac2f0b0d,192:4ESQiAjNf4ztnMk7Ih/Q3m5PYlizKkJShV5grwi/sSS9p:npNQinWkwSYp,48:8iZUmyAaq10P7PqVZl0OMKNQiWPCH+ka0OkGMRhBjOQkAcN+JAOAACkVjIu1/PEEA8eQElMcFl/RBIQKX:4ESQiqWPHOOycN2AOApE5PYliX,32
"only_1.txt",,2308,,ffec38581fa1e5aeeffdc727c1d7e43360544b9d4ed6a4fa5360a9606f4be164,,48:kJcinYn/4bRnyM5MC4LXv9svDGgGu7FcwfZD:kJK8Rp/4Mf7Fv,
"only_2.txt",4868,,425cc93977a5ab45d68bfbbcf47db69890b5192415f681e93a5672239f06830b,,48:xRnfu4bRnyK8Biur/SLhx+r9TLvngtSavS77GZ8xhhncR9l+G7jhk7hezS3bYuIZwXv9sv3uSu7Fcwi8E:H28RkSlwp3vngt7vC7GmPhcP7jhMhc4/7F6,,
"same-size.bin",4096,4096,87e250b1d97ca3e3f00f8a1a4496e0255d518f1452895966920683be9aa9894e,3cfd9c381a29799fa867423a9bfd22c029abf97535fa92dd49c5509bda18d95c,48:ePE4qp57vOugqNgDoXx82IiyZOV7ydyGUl7ar8ChOqCll5X3YKWoBwwxi/HMhIDcWSY6MAJkRlb0Yt09mqsa0DcUO14MUov9+27XA8IPR1:eA16roh8U46qS9hiwWSpskqI7uR1,48:ycesgHbY/WWgGefrxFA9aFLLrwssIy7ss/3gCEBGMfgjyXKBfL6aLYejKTGn41dqb9nFcMLm0SGpWKf2zdlb0cQY:9gkPTs8VgLCbp47w+dlbkY,18
"same-size.txt",5536,5536,43c99e8c43dd1045044dddfeb328dafe81773041fca17af0e8e016f7350e026a,dd32418c480cdc036419f628342bc0cd8907a30bc9d1c0daed728b7bf6a66ac4,48:CfISABuDNYmFc2UfeQzgN+PqmUat1mH/JFOg44AImT6209GBf/6CYMan/MdNdv9GiJJH7Oz5GnexyBZhVtuAiy6FgzyDDFc7xjcm2R9vVsFl9viPvkEb7DiAlv:qJ/yfeBbaO/badFl3g9kODZSQ,48:j4n3H60UuN1YbBRY2/dRO1vKtPSo04Uc0wOMv15FGZ39p9B+Fxg7nbKxPuVhUg8HoYl0ok4PddA/xGk8Gff4BRCqLJUuyb8sJj2e3nQwT+iViHSrLl:cX6BdRTECRL1v4xbYhcR3VHl,22
"same.txt",66716,66716,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,768:ZIjZNmiOIC6Qs6RTQ0pZJPLZXO5HMGU9Z2eNsDl8C55uEXx4W4DaIMuPOL7DMLSSTWCw3/DAkHJyRb/iJ3VLm6DSX5IiyoGJV:+NmiOKQs6tQmZJPLZXpG62eNsDlt7BtMa5L7QLSSTWCwvDRHEb/7tyv,768:ZIjZNmiOIC6Qs6RTQ0pZJPLZXO5HMGU9Z2eNsDl8C55uEXx4W4DaIMuPOL7DMLSSTWCw3/DAkHJyRb/iJ3VLm6DSX5IiyoGJV:+NmiOKQs6tQmZJPLZXpG62eNsDlt7BtMa5L7QLSSTWCwvDRHEb/7tyv,100
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
