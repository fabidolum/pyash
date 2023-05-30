import pytest
from io import BytesIO
from pyash import main as pyash

inputstr = b"abcdef\n"
sha256_inputstr = "ae0666f161fed1a5dde998bbd0e140550d2da0db27db1d0e31e370f2bd366a57"

blabla0 = b"**** this is a comment\n"
blabla1 = b"* this is a comment #2\n"
blabla2 = b"// this is a comment with //\n"


# -----------------------------------------------------------------------------
# basic hash functions
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "option",
    [
        (BytesIO(inputstr), b"*"),
        (BytesIO(blabla0 + inputstr), b"*"),
        (BytesIO(blabla0 + inputstr + blabla1), b"*"),
        (BytesIO(blabla2 + inputstr + blabla2), b"//"),
    ],
)
def test_hash(option):
    """Test the hash function on strings with and w/o comments"""
    assert pyash.computehash(option[0], option[1]) == sha256_inputstr


def test_no_comment_hash_func():
    assert pyash.regular_computehash(BytesIO(inputstr), None) == sha256_inputstr


# -----------------------------------------------------------------------------
# hashing a file
# -----------------------------------------------------------------------------
filecontent = "abcdef\n"
blibli0 = "**** this is a comment\n"
blibli1 = "* this is a comment #2\n"
blibli2 = "// this is a comment with //\n"


@pytest.mark.parametrize(
    "option",
    [
        (filecontent, "*"),
        (blibli0 + filecontent, "*"),
        (blibli0 + filecontent + blibli1, "*"),
        (blibli2 + filecontent + blibli2, "//"),
    ],
)
def test_hash_singlefile(tmp_path, capsys, option):
    d = tmp_path / "infile.txt"
    d.write_text(option[0])
    pyash.main(argv=["--skip", option[1], str(d)])
    captured = capsys.readouterr()
    assert (
        captured.out == f"# -s {option[1]}\n" + sha256_inputstr + "  " + str(d) + "\n"
    )
    assert captured.err == ""


def test_hash_multifiles(tmp_path, capsys):
    c0 = tmp_path / "infile0.txt"
    c1 = tmp_path / "infile1.txt"
    c0.write_text(filecontent)
    c1.write_text(comment1)
    c1.write_text(comment1)
    c1.write_text(filecontent)
    pyash.main(argv=["--skip", "*", str(c0), str(c1)])
    captured = capsys.readouterr()
    assert (
        captured.out
        == "# -s *\n"
        + sha256_inputstr
        + "  "
        + str(c0)
        + "\n"
        + "# -s *\n"
        + sha256_inputstr
        + "  "
        + str(c1)
        + "\n"
    )
    assert captured.err == ""


# -----------------------------------------------------------------------------
# testing the hash check
# -----------------------------------------------------------------------------
comment1 = "* this is a comment #2\n"
badcomment = "// bla\n"


@pytest.mark.parametrize(
    (
        "content",
        "status",
    ),
    [
        ("nope", 1),
        (filecontent, 0),
        (comment1 + filecontent + comment1, 0),
        (badcomment + filecontent + comment1, 1),
    ],
)
def test_check_singlefile(tmp_path, capsys, content, status):
    out = " FAILED\n"
    if status == 0:
        out = " OK\n"
    c = tmp_path / "infile.txt"
    c.write_text(content)
    d = tmp_path / "check.txt"
    checkfilecontent = "# -s *\n" + sha256_inputstr + "  " + str(c)
    d.write_text(checkfilecontent)
    # explicit skip
    r = pyash.main(argv=["-c", "--skip", "*", str(d)])
    captured0 = capsys.readouterr()
    assert captured0.out == str(c) + out
    assert captured0.err == ""
    assert r == status
    # implicit skip
    e = pyash.main(argv=["-c", str(d)])
    captured1 = capsys.readouterr()
    assert captured1.out == str(c) + out
    assert captured1.err == ""
    assert e == status


def test_check_multifiles(tmp_path, capsys):
    c0 = tmp_path / "infile0.txt"
    c1 = tmp_path / "infile1.txt"
    c0.write_text(filecontent)
    c1.write_text(comment1)
    c1.write_text(comment1)
    c1.write_text(filecontent)

    d = tmp_path / "check.txt"
    pyash.main(argv=["--skip", "*", str(c0), str(c1)])
    captured = capsys.readouterr()
    d.write_text(captured.out)
    r = pyash.main(argv=["-c", "--skip", "*", str(d)])
    assert r == 0
    e = pyash.main(argv=["-c", str(d)])
    assert e == 0
