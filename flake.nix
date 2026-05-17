{
  description = "Rule 110 compiler - Brainfuck to Rule 110 via Cook (2004)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.python313
          pkgs.python313Packages.pytest
          pkgs.python313Packages.numpy
        ];
      };
    };
}
