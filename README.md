# pyash

Custom sha256 hash tool to generate and check file hashs, while ignoring some comment lines.

## Features

This tool main feature is to ignore some lines to compute the sum. When computing thc checksums, the `` -s 'chars' `` option ot the command line indicates that the comments lines to ignore starts with 'chars' (can be single or multiple characters)

The output format is compliant with GNU sha256sum:

 * *pyash* can read the output of GNU sha256sum to check the files
 * *sha256sum* can read the output of *pyash* to check the files

The command line options are compliant with GNU sha256sum:

 * -c : read checksum from files and check them
 * --quiet : don't print OK for each successfully verified file

By default, *pyash* has a non 0 exit code if:

 * a checksum line is malformed
 * a checksum line does not match the computed sum of the file

 
## Install

Clone the main git repository:

    git clone git@github.com:fabidolum/pyash.git

You can install and run in the [poetry](https://python-poetry.org/) envirronement:

    poetry install
    poetry run pyash --help

Or build the *pyash* wheel package using [poetry](https://python-poetry.org/) and install the wheel with pip:

    poetry build
    python3 -m pip install --user dist/pyash-0.1.0-py3-none-any.whl


## Running

    pyash -h
    usage: pyash [-h] [-c] [-s SKIP] [-q] [--strict] filelist [filelist ...]

    Checksum (sha256sum) while skipping commented lines

    positional arguments:
    filelist              list of files for checksum computation or check

    options:
    -h, --help            show this help message and exit
    -c, --check           read SHA256 sums from the filelist and check them
    -s SKIP, --skip SKIP  start of line characters to consider as a comment
    -q, --quiet           don't print OK for each successfully verified file
    --strict              Placeholder option for compatibility with sha256sum


## Example

This example is on simple (SPICE) files, the comment is defined by a '\*' at the start of the line.

    cat file0.sp 
    * some comment
    .subckt test a b
    r0 a b 0.001
    .ends test

    cat file1.sp 
    * some other comment
    .subckt test a b
    r0 a b 0.001
    .ends test
    * created on 2023-04-06

    cat file2.sp 
    .subckt test a b
    r0 a b 0.001
    .ends test

Each of this files has a different checksum:

    sha256sum file0.sp file1.sp file2.sp
    15d80aadb2b3ffe686b100f12e66ad29e83fbd7dea296a6937b2c8b986050639  file0.sp
    1e03ad61e0826c8840d3c547ef5bd8a076b15f006c7127164fd54b8bc6214dab  file1.sp
    2bb5821355a8bd0b639ecba2dfc543b65e68bdc12d5feaad832e24f6fb1f967e  file2.sp

Now running ``pyash`` and skipping the comment lines:

    pyash -s '*' file0.sp file1.sp file2.sp
    # -s *
    2bb5821355a8bd0b639ecba2dfc543b65e68bdc12d5feaad832e24f6fb1f967e  file0.sp
    # -s *
    2bb5821355a8bd0b639ecba2dfc543b65e68bdc12d5feaad832e24f6fb1f967e  file1.sp
    # -s *
    2bb5821355a8bd0b639ecba2dfc543b65e68bdc12d5feaad832e24f6fb1f967e  file2.sp

Since the ``file2.sp`` does not have any comment line, the usual ``sha256sum`` gives the same checksum than ``pyash`` (which is expected).

To verify a checksum, the ``--skip`` parameter is optional if the checksum file has been created with ``pyash``.

    pyash -c checkfile.txt
    file0.sp OK
    file1.sp OK
    file2.sp OK



## Limitations

 * comments are defined by the first character(s) of the line. Therefore, there is no support for multi-lines comment, or end-of-line comments.
 * it's slow: yes, it's written in Python, much slower than [GNU sha256sum](https://www.gnu.org/software/coreutils/). 
 * this tools support only a subset of the GNU sha256sum.

## FAQ

**Q**: Why such a tool ?

**A**: I need to check if the *content* of a file changes, but I want to skip the eventual changes in the comment lines. My most common case is to check if a SPICE netlist is unchanged, but the netlister tool keeps inserting a timestamp in the comments each time the tool is run. 

**Q**: Why Python ? it's slow.

**A**: Because I need a working prototype, and speed is not my main concern (for now).

**Q**: Is it secure ? Can I use it for (insert anything cryptographic related) ?

**A**: No. The sole purpose is to hash files to check if their content changes. This tool is using the Python standard library [hashlib](https://docs.python.org/3/library/hashlib.html) to compute the sha256 control sum.

**Q**: Why sha256 and not any other ?

**A**: No good answer here. I just need to avoid collision, maybe MD5 would be enough.

