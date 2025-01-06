{
  pkgs,
}:
pkgs.mkShellNoCC {
  packages = with pkgs; [
    (python3.withPackages (ps: [
      ps.caldav
      ps.selenium
      ps.xvfbwrapper
    ]))
    chromium
    chromedriver
    xorg.xvfb
    # This is also useful during development
    xvfb-run
  ];
}
