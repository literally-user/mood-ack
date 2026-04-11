from sqlalchemy import MetaData
from sqlalchemy.orm import registry

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

# your_table = Table(
#     "your_table",
#     metadata,
# )


def start_mapper() -> None:
    # registry_mapper.map_imperatively(YourClass, user_account_table)
    pass
