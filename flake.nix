{
  description = "Tool to scrape Disney World Fireworks showtimes";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-24.11";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.callPackage ./package.nix { };
      devShells.${system}.default = import ./shell.nix { inherit pkgs; };
      apps.${system}.caldav = {
        type = "app";
        program = "${self.packages.${system}.default}/bin/disney-fireworks-caldav";
      };

      overlays.default = final: prev: {
        # TODO: Put under `python3Packages`?
        disney-fireworks-scraper = self.packages.${system}.default;
      };
      nixosModules.caldav = import ./module-caldav.nix;
      nixosModules.google = import ./module-google.nix;

      formatter.${system} = pkgs.nixfmt-rfc-style;
    };
}
