from enum import IntEnum
from functools import wraps


class CommitMode(IntEnum):
    """
    Commit modes for the managed db methods
    """

    NONE = 0
    FLUSH = 1
    COMMIT = 2
    ROLLBACK = 3


def menage_db_method(auto_commit: CommitMode = CommitMode.FLUSH):
    def decorator(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            result = f(self, *args, **kwargs)
            match auto_commit:
                case CommitMode.FLUSH:
                    self.session.flush()
                case CommitMode.COMMIT:
                    self.session.commit()
                case CommitMode.ROLLBACK:
                    self.session.rollback()

            return result

        return wrapped_f

    return decorator
