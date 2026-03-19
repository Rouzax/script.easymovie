from resources.lib.ui.main import main, _handle_entry_args

try:
    if not _handle_entry_args("script.easymovie"):
        main()
except SystemExit:
    pass
except Exception:
    try:
        from resources.lib.utils import get_logger
        log = get_logger('default')
        log.exception("Unhandled error in EasyMovie", event="ui.crash")
    except Exception:
        import traceback
        import xbmc
        xbmc.log(
            f"[EasyMovie] Unhandled error: {traceback.format_exc()}",
            xbmc.LOGERROR,
        )
