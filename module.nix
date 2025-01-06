{
  lib,
  pkgs,
  config,
  ...
}:
with lib;
let
  cfg = config.services.disney-fireworks-caldav;
in
{
  options.services.disney-fireworks-caldav = {
    enable = mkEnableOption "Disney fireworks CalDav sync service";
    package = mkPackageOption pkgs "disney-fireworks-scraper" { };

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
      CALDAV_URL = mkOption {
        type = types.str;
        description = "CalDav URL to sync with";
      };
    };

    secretsFile = mkOption {
      type = types.path;
      description = ''
        Configuration file containing secrets.

        Must include:
        - CALDAV_USERNAME
        - CALDAV_PASSWORD
        - CALENDAR_ID
      '';
    };
  };

  config = mkIf cfg.enable {
    systemd.services.disney-fireworks-caldav-job = {
      description = "Cron job to sync 1 weeks worth of Disney fireworks events";
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      wantedBy = [ "multi-user.target" ];

      environment = cfg.settings;

      serviceConfig = {
        Type = "oneshot";
        DynmicUser = true;
        UMask = "0077";
        WorkingDirectory = cfg.dataDir;
        # TODO: Use LoadCredential instead?
        EnvironmentFile = [ cfg.secretsFile ];
        ExecStart = "${cfg.package}/bin/disney-fireworks-caldav";
        SuccessExitStatus = [ "0" ];
        # TODO: SystemD hardening
      };
    };
    systemd.timers.disney-fireworks-caldav-job = {
      wantedBy = [ "timers.target" ];
      description = "Run Disney Fireworks CalDav sync regularly";
      timerConfig = {
        OnCalendar = cfg.syncTimer;
        RandomizedDelaySec = cfg.randomizedDelaySec;
        Persistent = true;
      };
    };
  };
}
