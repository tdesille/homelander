{ pkgs, lib, config, inputs, ... }:

{

  # https://devenv.sh/packages/
  packages = [ pkgs.git
  pkgs.uv
  pkgs.ruff ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    uv.enable = true;
    version = "3.13";
  };
}