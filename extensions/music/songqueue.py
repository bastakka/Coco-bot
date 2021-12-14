import asyncio
import itertools
import random
from typing import Union
from .song import Song

class SongQueue(asyncio.Queue):
    """Class for SongQueue"""

    def __getitem__(self, item) -> Union[Song, list]:
        """Get item from queue"""
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        return self._queue[item]

    def __iter__(self) -> iter:
        """Iterate over queue"""
        return iter(self._queue)

    def __len__(self) -> int:
        """Get length of queue"""
        return self.qsize()

    def clear(self) -> None:
        """Clear queue"""
        self._queue.clear()

    def shuffle(self) -> None:
        """Shuffle queue"""
        random.shuffle(self._queue)

    def remove(self, index: int) -> Song:
        """Remove song from queue"""
        del self._queue[index]