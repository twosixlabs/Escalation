from abc import ABC, abstractmethod

from utility.constants import TITLE, DESCRIPTION, TYPE, BOOLEAN
from utility.schema_utils import SchemaDataHolder


class DataConfigInterfaceBuilder(ABC):
    def __init__(self, data_holder: SchemaDataHolder):
        self.data_holder = data_holder

        self.user_selectable_dict = {
            TITLE: "User selectable",
            DESCRIPTION: "Allow user to change property on dashboard page.",
            TYPE: BOOLEAN,
        }

    @staticmethod
    @abstractmethod
    def build_data_sources_schema(data_source_names, possible_column_names):
        raise NotImplementedError

    @abstractmethod
    def build_data_filter_schema(self):
        raise NotImplementedError
