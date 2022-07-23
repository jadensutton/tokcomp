STATUS = {'PENDING': 'Pending', 'COMPLETE': 'Complete', 'FAILED': 'Failed'}
STATUS_MESSAGES = {'PENDING': 'Your compilation is rendering, please check back later.', 'COMPLETE': 'Your compilation is ready to download.', 'FAILED': "Render failed. Please make sure all TikTok share URL's are valid"}

class ExportUtils:
    def get_pending_status(self):
        return STATUS['PENDING']

    def get_complete_status(self):
        return STATUS['COMPLETE']

    def get_failed_status(self):
        return STATUS['FAILED']

    def get_pending_status_message(self):
        return STATUS_MESSAGES['PENDING']

    def get_complete_status_message(self):
        return STATUS_MESSAGES['COMPLETE']

    def get_failed_status_message(self):
        return STATUS_MESSAGES['FAILED']
