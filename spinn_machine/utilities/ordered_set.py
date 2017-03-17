from spinn_utilities.ordered_set import OrderedSet
import logging

logger = logging.getLogger(__name__)
logger.warn("Deprecation Warning: OrderedSet has moved to SpiNNUtils.")

__all__ = ["OrderedSet"]
