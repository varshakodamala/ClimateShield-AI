from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """Abstract base class for data extractors."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Extract data from source.

        Returns:
            Dict containing extracted data or None if extraction fails
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate connection to data source.

        Returns:
            True if connection is valid, False otherwise
        """
        pass
