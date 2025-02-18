{
  lib,
  pkgs,
  config,
  ...
}:
with lib;
let
  cfg = config.services.disney-fireworks-google;
in
{
  options.services.disney-fireworks-google = {
    enable = mkEnableOption "Disney fireworks Google Calendar sync service";
    package = mkPackageOption pkgs "disney-fireworks-scraper" { };
    chromeBrowserPath = mkOption {
      type = types.str;
      description = ''
        Location of the Chrome/Chromium executable to use.
      '';
      default = "${pkgs.chromium}/bin/chromium";
    };
    chromeDriverPath = mkOption {
      type = types.str;
      description = ''
        Location of the chromedriver executable to use.
      '';
      default = "${pkgs.chromedriver}/bin/chromedriver";
    };

    syncTimer = mkOption {
      type = types.str;
      description = ''
        SystemD calendar trigger. Defaults to midnight every Monday
      '';
      default = "Mon *-*-* 00:00:00";
    };
    randomizedDelaySec = mkOption {
      type = types.int;
      description = ''
        SystemD `RandomizedDelaySec` for adding jitter to the timer
      '';
      default = 3600;
    };

    settings = {
      CALENDAR_ID = mkOption {
        type = types.str;
        description = "Calendar ID to sync with";
      };
      CALENDAR_EVENT_TIMEZONE = mkOption {
        type = types.str;
        description = "Override timezone of the events created";
      };
      CALENDAR_EVENT_NAME = mkOption {
        type = types.str;
        description = "Set a custom name for the events";
      };
    };

    settingsFile = mkOption {
      type = types.path;
      description = ''
        Environment variable file containing the same fields as `settings`.

        Useful for settings that can change over time without re-building config.
      '';
    };

    credentialsFile = mkOption {
      type = types.path;
      description = "Google Cloud Service Account credentials file path.";
    };
  };

  config = mkIf cfg.enable {
    systemd.services.disney-fireworks-google = {
      description = "Oneshot task to sync 1 weeks worth of Disney fireworks events";
      after = [ "network-online.target" ];

      environment = {
        CHROME_BROWSER_PATH = cfg.chromeBrowserPath;
        CHROME_DRIVER_PATH = cfg.chromeDriverPath;
        CREDENTIALS_FILE = cfg.credentialsFile;
      } // cfg.settings;

      serviceConfig = {
        Type = "oneshot";
        DynamicUser = true;
        UMask = "0077";
        EnvironmentFile = mkIf (cfg.settingsFile != null) [ cfg.settingsFile ];
        ExecStart = "${cfg.package}/bin/disney-fireworks-google";
        SuccessExitStatus = [ "0" ];
        # TODO: SystemD hardening
      };
    };
    systemd.timers.disney-fireworks-google = {
      wantedBy = [ "timers.target" ];
      description = "Run Disney Fireworks Google Calendar sync regularly";
      timerConfig = {
        OnCalendar = cfg.syncTimer;
        RandomizedDelaySec = cfg.randomizedDelaySec;
        Persistent = true;
      };
    };
  };
}
