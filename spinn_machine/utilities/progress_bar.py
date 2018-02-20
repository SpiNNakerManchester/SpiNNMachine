from spinn_utilities.progress_bar import ProgressBar
import logging

logger = logging.getLogger(__name__)
logger.warning("Deprecation Warning: ProgressBar has moved to SpiNNUtils.")

__all__ = ["ProgressBar"]
