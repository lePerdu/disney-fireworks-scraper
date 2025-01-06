{
  lib,
  python3Packages,

  bash,
  chromedriver,
  chromium,
  xorg,
}:
with python3Packages;
buildPythonApplication {
  pname = "disney-fireworks-scraper";
  version = "0.0.1";
  src = ./.;

  format = "pyproject";
  nativeBuildInputs = [ setuptools ];
  dependencies = [
    caldav
    selenium
    xvfbwrapper
  ];

  makeWrapperArgs = [
    "--prefix PATH : ${
      lib.makeBinPath [
        # A shell is used internally by selenium when finding browser/driver paths
        # TODO: Specify browser paths explicitly to avoid needing this (and also
        # allow overriding them via the module config?)
        bash
        chromedriver
        chromium
        xorg.xvfb
      ]
    }"
  ];
}
