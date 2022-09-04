class ExportObjectMapper:
    def __init__(self):
        pass

    def transport_to_persistence(self, source: dict, user_id: str, export_id: str) -> dict:
        target = {}

        if export_id:
            target['_id'] = export_id

        if user_id:
            target['created_by'] = user_id

        if 'title' in source:
            target['title'] = source['title']

        if 'compilation_id' in source:
            target['compilation_id'] = source['compilation_id']

        if 'created_at' in source:
            target['created_at'] = source['created_at']

        if 'status' in source:
            target['status'] = source['status']

        if 'status_message' in source:
            target['status_message'] = source['status_message']

        return target

    def persistence_to_transport(self, source: dict) -> dict:
        target = {}

        if '_id' in source:
            target['id'] = source['_id']

        if 'title' in source:
            target['title'] = source['title']

        if 'created_at' in source:
            target['created_at'] = source['created_at']

        if 'status' in source:
            target['status'] = source['status']

        if 'status_message' in source:
            target['status_message'] = source['status_message']

        return target
