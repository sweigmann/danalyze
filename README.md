# danalyze

danalyze - recursive differential analysis on files

Given two directories, `danalyze` recursively analyzes all files
within them and computes sizes, sha256 and ssdeep hashes. 
The CSV formatted results are dumped to the console.

## usage:

```bash
danalyze [-h] [--version] dir1 dir2

Recursive differential analysis on files

positional arguments:
  dir1
  dir2

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```

## example:

```bash
danalyze.py test/1 test/2
```

```csv
filepath,file1_size,file2_size,file1_sha256,file2_sha256,file1_ssdeep,file2_ssdeep,ssdeep_score
"cicero.txt",1792,1819,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,77bb2c0d3092238e822dc16b6a7dbe72a51d99701e5289ad71da02dc28fc76c6,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,24:DGxpjKhOdoqE/2JnkZWevVPjNk/08WtqnNjUAHDe6gJWtf7VMvGbGiDs+lHV2zkc:ULWqrSPtG/DKThJAqvGbGIlHVakIm+,80
"different.txt",1792,2027,ed253f478d78bfe80187801a71142af178f484bcb58d40616582baf08ddd2c15,6f0cf13873ab282eaedd2d70bb705db7aab97879df9e10ae8f1afe48e4b451f6,24:DkxpjKhOdoqE/2JnkZWevVPjKk/dbWtq3NjJpThDe6gJWtf7VMvGbGiDOlHV2RI1:SLWqrSPtR/lrGhJAqvGbGrlHVYIm+,24:DEPLi28PUOO7v20dvgBX5mtHNIYJVETYHVVTUWbrnFFmVVmKLruL9lirAb2T1SSL:p0ePzUNzWY1yWbCVVmKQN0oSiuNzbSeT,0
"only_1.txt",2308,,ffec38581fa1e5aeeffdc727c1d7e43360544b9d4ed6a4fa5360a9606f4be164,,48:sYr8tJBA8xh5hWJmu2Cc+sj+t017jWy/LpLYs:sYr8tJBjhyj8hN,,
"only_2.txt",,4868,,425cc93977a5ab45d68bfbbcf47db69890b5192415f681e93a5672239f06830b,,96:DHmBrBkIqMmnoCUtgfd5nyliuy/yJ6YzmnS+:jYrqI4noCUtGny7y/y4Yzm1,
"same.txt",66716,66716,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,b4ac7bf7357f0e581a1e872b64a3f89b1586f0747e97e1113651dd178d0f95b3,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,768:NomyJOjFk+mDEEqm3fR+2f7Kz05jAKYzhwyhaVEA4xJUWuuvm8Ty/tZ3Iw8emkmm:0SF1m35++vo3uueCy/c4mjm,100
```
