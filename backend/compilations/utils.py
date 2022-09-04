COMPILATION_REQUIRED_FIELDS = {'title', 'videos', 'background'}
DEFAULT_BACKGROUND = 'Default TokComp Background'

class CompilationUtils:
    def get_required_fields(self):
        return COMPILATION_REQUIRED_FIELDS

    def get_default_background(self):
        return DEFAULT_BACKGROUND
