{
  lib,
  python3Packages,

  chromium,
  chromedriver,
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
    "--prefix PATH : ${lib.makeBinPath [ chromium chromedriver xorg.xvfb ]}"
  ];
}
