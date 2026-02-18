# //////////////////////////////////////////////////////////////////////////////
class Utils:
    @staticmethod
    def prev_cyclic(current: int, maxval: int) -> int | None:
        if current == 0: return
        if current is None: return maxval - 1
        return current - 1

    # --------------------------------------------------------------------------
    @staticmethod
    def next_cyclic(current: int, maxval: int) -> int | None:
        if current == maxval - 1: return
        if current is None: return 0
        return current + 1


# //////////////////////////////////////////////////////////////////////////////
