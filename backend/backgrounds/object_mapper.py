class BackgroundObjectMapper:
    def __init__(self):
        pass

    def transport_to_persistence(self, source: dict, user_id: str, background_id: str) -> dict:
        target = {}

        if background_id:
            target['_id'] = background_id

        if user_id:
            target['created_by'] = user_id

        if 'name' in source:
            target['name'] = source['name']

        if 'file' in source:
            target['file'] = source['file']

        return target

    def persistence_to_transport(self, source: dict) -> dict:
        target = {}

        if '_id' in source:
            target['_id'] = source['_id']

        if 'name' in source:
            target['name'] = source['name']

        if 'file' in source:
            target['file'] = source['file']

        return target
