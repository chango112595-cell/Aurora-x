# Copyright 2019-2025 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import structlog

from nwastdlib.settings import nwa_settings

logger = structlog.get_logger()


def start_debugger() -> None:
    """Start a debug server for VSCode/PyCharm to attach to, if configured.

    For usage see https://github.com/workfloworchestrator/nwa-stdlib/blob/main/docs/debugging.md
    """
    if nwa_settings.DEBUG_VSCODE:
        import debugpy  # noqa: T100

        debugpy_kwargs = ("127.0.0.1", nwa_settings.DEBUG_VSCODE_PORT)
        logger.info("Starting debugpy", debugpy_kwargs=debugpy_kwargs)
        debugpy.listen(debugpy_kwargs)  # noqa: T100
        logger.info("Waiting for debug client to connect")
        debugpy.wait_for_client()  # noqa: T100
        logger.info("Debug client connected")
    elif nwa_settings.DEBUG_PYCHARM:
        # trick to get around debug-statements pre-commit error: pydevd_pycharm imported
        pydevd_pycharm = __import__("pydevd_pycharm")

        port = nwa_settings.DEBUG_PYCHARM_PORT
        pydevd_kwargs = {"host": "127.0.0.1", "port": port, "stdoutToServer": True, "stderrToServer": True}
        logger.info("Connecting to pydevd server (choose 'Resume Program' in PyCharm)", pydevd_kwargs=pydevd_kwargs)
        pydevd_pycharm.settrace(**pydevd_kwargs)
        logger.info("Connected to pydevd server")
    else:
        logger.info("No debugger configured")
