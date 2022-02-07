from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class Subject:
    """
    Subject part of the observer design pattern. When a note-worthy event occurs, the `notify` method should be called.
    """

    def __init__(self):
        """Initialize the subject.
        """        
        self.observers = [] # type: List[Observer]

    def attach(self, observer: Observer) -> None:
        """Attach an observer to the subject.

        Args:
            observer (Observer): The observer to attach.
        """        
        self.observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Detach an observer from the subject.

        Args:
            observer (Observer): The observer to detach.
        """        
        self.observers.remove(observer)

    def notify(self) -> None:
        """Notify all observers about an event.
        """        
        for observer in self.observers:
            observer.update(self)

class Observer(ABC):
    """
    Observer part of the observer design pattern. Override the the `update` method to use this class.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """Method called by the subject when an event happens.

        Args:
            subject (Subject): The subject that called this method.
        """
        pass