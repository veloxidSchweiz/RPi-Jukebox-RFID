"""
Miscellaneous function package
"""
import copy
import os
import time
import logging.handlers
import jukebox
import jukebox.plugs as plugin
import jukebox.utils
from jukebox.daemon import get_jukebox_daemon

logger = logging.getLogger('jb.misc')


@plugin.register
def rpc_cmd_help():
    """Return all commands for RPC"""
    return plugin.summarize()


@plugin.register
def get_all_loaded_packages():
    """Get all successfully loaded plugins"""
    return plugin.get_all_loaded_packages()


@plugin.register
def get_all_failed_packages():
    """Get all plugins with error during load or initialization"""
    return plugin.get_all_failed_packages()


def _to_jsonable(obj):
    """Convert config data to JSON-serializable types (ruamel.yaml may leave custom types)."""
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return str(obj)


def _build_plugin_details(loaded, callables_map, config_keys):
    """Build per-package details: callables (RPC functions) and whether a config exists for that name."""
    details = {}
    for fullname, entry in callables_map.items():
        pkg = entry.get('package')
        if pkg not in loaded:
            continue
        if pkg not in details:
            details[pkg] = {
                'callables': [],
                'has_config': pkg in config_keys,
            }
        details[pkg]['callables'].append({
            'fullname': fullname,
            'plugin': entry.get('plugin'),
            'method': entry.get('method'),
            'signature': entry.get('signature', ''),
            'description': (entry.get('description') or '').strip()[:200],
        })
    for pkg in details:
        details[pkg]['callables'].sort(key=lambda x: x['fullname'])
    return details


@plugin.register
def get_debug_info():
    """Return debug info: plugin status (loaded/failed), callables per package, and configuration."""
    loaded = plugin.get_all_loaded_packages()
    failed = plugin.get_all_failed_packages()
    config = {}
    try:
        import jukebox.cfghandler as cfghandler
        for name, cfg in list(cfghandler.handlers.items()):
            with cfg:
                data = _to_jsonable(copy.deepcopy(cfg._data))
            config[name] = {'file': cfg.loaded_from, 'data': data}
    except Exception as e:
        logger.warning(f"get_debug_info: could not read config handlers: {e}")

    callables_map = {}
    try:
        callables_map = plugin.summarize()
    except Exception as e:
        logger.warning(f"get_debug_info: could not summarize callables: {e}")

    config_keys = set(config.keys())
    details = _build_plugin_details(loaded, callables_map, config_keys)

    return {
        'plugins': {
            'loaded': loaded,
            'failed': failed,
            'details': details,
        },
        'config': config,
    }


@plugin.register
def get_start_time():
    """Time when JukeBox has been started"""
    return time.ctime(get_jukebox_daemon().start_time)


def get_log(handler_name: str):
    """Get the log file from the loggers (debug_file_handler, error_file_handler)"""
    # With the correct logger.yaml, there is up to two RotatingFileHandler attached
    content = "No file handles configured"
    for h in logging.getLogger('jb').handlers:
        if isinstance(h, logging.handlers.RotatingFileHandler):
            content = f"No file handler with name {handler_name} configured"
            if h.name == handler_name:
                try:
                    size = os.path.getsize(h.baseFilename)
                    if size == 0:
                        content = f"Log file {h.baseFilename} is empty. (Could be good or bad: " \
                                  "Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?)"
                        break
                    mtime = os.path.getmtime(h.baseFilename)
                    stime = get_jukebox_daemon().start_time
                    logger.debug(f"Accessing log file {h.baseFilename} modified time {time.ctime(mtime)} "
                                 f"(JB start time {time.ctime(stime)})")
                    # Generous 3 second tolerance between file creation and jukebox start time recording
                    if mtime - stime < -3:
                        content = (f"Log file {h.baseFilename} too old for this Jukebox start! "
                                   f"Is the RotatingFileHandler configured as handler sink for jb in logger.yaml?")
                        break
                    with open(h.baseFilename) as stream:
                        content = stream.read()
                except Exception as e:
                    content = f"{e.__class__.__name__}: {e}"
                    logger.error(content)
                break
    return content


@plugin.register
def get_log_debug():
    """Get the log file (from the debug_file_handler)"""
    return get_log('debug_file_handler')


@plugin.register
def get_log_error():
    """Get the log file (from the error_file_handler)"""
    return get_log('error_file_handler')


@plugin.register
def get_version():
    return jukebox.version()


@plugin.register
def get_git_state():
    """Return git state information for the current branch"""
    return get_jukebox_daemon().git_state


@plugin.register
def empty_rpc_call(msg: str = ''):
    """This function does nothing.

    The RPC command alias 'none' is mapped to this function.

    This is also used when configuration errors lead to non existing RPC command alias definitions.
    When the alias definition is void, we still want to return a valid function to simplify error handling
    up the module call stack.

    :param msg: If present, this message is send to the logger with severity warning
    """
    if msg:
        logger.warning(msg)
