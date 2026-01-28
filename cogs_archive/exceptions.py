class LabArchiveError(Exception):
    pass


class RegistryError(LabArchiveError):
    pass


class ZenodoError(LabArchiveError):
    pass


class ChecksumError(LabArchiveError):
    pass
