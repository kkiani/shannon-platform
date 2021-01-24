from typing import Any, Dict
from serial import Serial
from threading import Thread

from shannon_platform.base.notification_center import NotificationCenter, NotificationDefaultNames
from shannon_platform.base.metaclasses import Singleton


class SerialService(metaclass=Singleton):
    __adaptor = Serial(port='/dev/cu.usbmodem14301', baudrate=9600)

    def __init__(self) -> None:
        super().__init__()

        NotificationCenter().add_observer(name=NotificationDefaultNames.DATA_SEND, callback=self.write)

        serial_read_thread = Thread(target=self.read)
        serial_read_thread.start()
        
    def read(self):
        while True:
            data = self.__adaptor.read(2)
            
            if len(data) < 2:
                return

            NotificationCenter().post(
                name=NotificationDefaultNames.DATA_RECEIVE, 
                user_info={
                    'id': data[0],
                    'value': data[1]
                }
            )

    def write(self, user_info: Dict[str, Any]):
        command = bytes([user_info['id'], user_info['value']])
        self.__adaptor.write(command)