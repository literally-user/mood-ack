from pathlib import Path

from prodik.application.errors import UnsupportedFileExtensionError
from prodik.domain.task import FileId
from prodik.infrastructure.config import ObjectStorageConfig
from prodik.infrastructure.file import FileProcessingRegistry


class FileReader:
    config: ObjectStorageConfig
    file_processing_registry: FileProcessingRegistry

    def __init__(
        self,
        config: ObjectStorageConfig,
        file_processing_registry: FileProcessingRegistry,
    ) -> None:
        self.file_processing_registry = file_processing_registry
        self.config = config

    def process(self, file_id: FileId) -> str:
        with Path.open(self.config.temp_directory / file_id, "r") as file:
            processing_client = self.file_processing_registry.get_client(
                file_id.split(".")[-1]
            )
            if processing_client is None:
                raise UnsupportedFileExtensionError("Unsupported file extension")

            return processing_client.process(file.read())
