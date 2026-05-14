import subprocess
import sys
import time
import os
from logger import log_error, log_info, log_warning


MAX_RESTARTS   = 5    # Max restarts before giving up
RESTART_DELAY  = 3    # Seconds between restarts
restart_count  = 0


def run_jarvis():
    """Run JARVIS and auto-restart if it crashes"""
    global restart_count

    log_info("=" * 50)
    log_info("  J.A.R.V.I.S Auto-Restart System Active")
    log_info("=" * 50)

    while restart_count < MAX_RESTARTS:
        log_info(f"Starting JARVIS (attempt {restart_count + 1})...")

        try:
            # Run main.py as subprocess
            process = subprocess.run(
                [sys.executable, "main.py"],
                cwd=os.getcwd()
            )

            # Check exit code
            if process.returncode == 0:
                log_info("JARVIS shut down normally.")
                break

            else:
                restart_count += 1
                log_warning(
                    f"JARVIS crashed! (exit code {process.returncode})"
                    f" Restart {restart_count}/{MAX_RESTARTS}"
                )

                if restart_count < MAX_RESTARTS:
                    log_info(f"Restarting in {RESTART_DELAY} seconds...")
                    time.sleep(RESTART_DELAY)
                else:
                    log_error("Max restarts reached. Please check logs.")

        except KeyboardInterrupt:
            log_info("JARVIS manually stopped. Goodbye!")
            break

        except Exception as e:
            log_error(f"Auto-restart error: {e}")
            restart_count += 1
            time.sleep(RESTART_DELAY)


if __name__ == "__main__":
    run_jarvis()