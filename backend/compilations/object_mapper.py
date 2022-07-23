class CompilationObjectMapper:
    def __init__(self):
        pass

    def transport_to_persistence(self, source: dict, user_id: str, compilation_id: str) -> dict:
        target = {}

        if user_id:
            target['_id'] = compilation_id

        if compilation_id:
            target['created_by'] = user_id

        if 'title' in source:
            target['title'] = source['title']

        if 'videos' in source:
            target['videos'] = source['videos']

        if 'created_at' in source:
            target['created_at'] = source['created_at']

        if 'modified_at' in source:
            target['modified_at'] = source['modified_at']

        return target

    def persistence_to_transport(self, source: dict) -> dict:
        target = {}

        if source['_id']:
            target['id'] = source['_id']

        if 'title' in source:
            target['title'] = source['title']

        if 'videos' in source:
            target['videos'] = source['videos']

        if 'created_at' in source:
            target['created_at'] = source['created_at']

        if 'modified_at' in source:
            target['modified_at'] = source['modified_at']

        return target
