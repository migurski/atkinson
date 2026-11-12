"""Verify the real installed protocol package and strict public call contracts."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def execute(label: str, command: list[str], output: Path, expected: int = 0) -> subprocess.CompletedProcess[str]:
    """Run an unchanged analyzer and retain both complete output streams."""
    result = subprocess.run(command, cwd=output, capture_output=True, text=True, encoding="utf-8")
    (output / f"{label}.stdout.log").write_text(result.stdout, encoding="utf-8")
    (output / f"{label}.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != expected:
        raise RuntimeError(f"{label}: expected status {expected}, got {result.returncode}; see retained logs")
    return result


def main() -> None:
    """Check library sources, positive programs and every marked negative line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True)
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    output = Path.cwd() / "typing-contract-results"
    output.mkdir(exist_ok=False)
    for forbidden in ("PYTHONPATH", "MYPYPATH", "PYRIGHT_PYTHON_FORCE_VERSION", "PYRIGHT_PYTHON_IGNORE_WARNINGS", "PYTHON_GIL"):
        if forbidden in os.environ:
            raise RuntimeError(f"Unexpected analyzer/runtime override: {forbidden}")
    audit = (
        "import importlib,importlib.metadata,json,pathlib,sys,sysconfig; "
        "m=importlib.import_module(sys.argv[1]); p=pathlib.Path(m.__file__).resolve(); "
        "assert p.is_relative_to(pathlib.Path(sys.prefix).resolve()),p; "
        "assert (p.parent/'py.typed').is_file(); "
        "assert importlib.metadata.version(sys.argv[2])==sys.argv[3]; "
        "assert sysconfig.get_config_var('Py_GIL_DISABLED')==1; "
        "assert sys._is_gil_enabled() is False and sys._xoptions.get('gil') is None; "
        "print(json.dumps({'package':str(p.parent),'version':sys.argv[3],'python':sys.version,'executable':sys.executable}))"
    )
    installed = json.loads(execute("actual-installed-identity", [sys.executable, "-I", "-c", audit, args.module, args.distribution, args.version], output).stdout)
    mypy_version = execute("actual-mypy-version", [sys.executable, "-m", "mypy", "--version"], output).stdout
    pyright_version = execute("actual-pyright-version", [sys.executable, "-m", "pyright", "--version"], output).stdout
    if not mypy_version.startswith("mypy 2.4.1+stablekite.4"):
        raise RuntimeError(mypy_version)
    if "1.1.414-stablekite.3" not in pyright_version:
        raise RuntimeError(pyright_version)
    mypy_config = output / "mypy.ini"
    mypy_config.write_text("[mypy]\nstrict = True\npython_version = 3.15\nincremental = False\n", encoding="utf-8")
    pyright_config = output / "pyrightconfig.json"
    pyright_config.write_text(json.dumps({"typeCheckingMode": "strict", "pythonVersion": "3.15"}, indent=2) + "\n", encoding="utf-8")
    mypy = [sys.executable, "-m", "mypy", "--config-file", str(mypy_config)]
    pyright = [sys.executable, "-m", "pyright", "--project", str(pyright_config), "--pythonpath", sys.executable, "--outputjson"]
    execute("installed-library-mypy", [*mypy, "-p", args.module], output)
    library = json.loads(execute("installed-library-pyright", [*pyright, installed["package"]], output).stdout)
    if library["summary"]["filesAnalyzed"] < 2:
        raise RuntimeError("The installed library was not analyzed")
    for name in ("positive.py", "negative.py"):
        shutil.copyfile(source / "tests" / "typing" / name, output / name)
    execute("positive-mypy", [*mypy, str(output / "positive.py")], output)
    positive = json.loads(execute("positive-pyright", [*pyright, str(output / "positive.py")], output).stdout)
    if positive["summary"]["filesAnalyzed"] != 1:
        raise RuntimeError("The positive public program was not analyzed")
    execute("positive-real-native", [sys.executable, "-I", str(output / "positive.py")], output)
    negative_source = (output / "negative.py").read_text(encoding="utf-8")
    expected = [number for number, line in enumerate(negative_source.splitlines(), 1) if "# EXPECT_ERROR" in line]
    if not expected:
        raise RuntimeError("No genuine negative controls were marked")
    result = execute("negative-mypy", [*mypy, str(output / "negative.py")], output, expected=1)
    mypy_lines = sorted({int(number) for number in re.findall(r"negative\.py:(\d+): error:", result.stdout)})
    result = execute("negative-pyright", [*pyright, str(output / "negative.py")], output, expected=1)
    diagnostics = json.loads(result.stdout)
    pyright_lines = sorted({item["range"]["start"]["line"] + 1 for item in diagnostics["generalDiagnostics"] if item["severity"] == "error"})
    if mypy_lines != expected or pyright_lines != expected:
        raise RuntimeError(f"Negative contract lines mismatch: {expected}, {mypy_lines}, {pyright_lines}")
    result = {"status": "PASS_INSTALLED_REAL_PUBLIC_TYPES_AND_ALL_STRICT_NEGATIVE_LINES", "installed": installed, "negative_error_lines_each_checker": expected, "mypy_version": mypy_version.strip(), "pyright_version": pyright_version.strip()}
    (output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
