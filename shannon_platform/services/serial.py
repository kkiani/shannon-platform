from typing import Any, Dict
from serial import Serial
from threading import Thread
import time

from shannon_platform.base.notification_center import NotificationCenter, NotificationDefaultNames
from shannon_platform.base.metaclasses import Singleton


class SerialService:
    def __init__(self, port: str) -> None:
        self.__adaptor = Serial(port=port, baudrate=9600)

        NotificationCenter().add_observer(name=NotificationDefaultNames.DATA_SEND, callback=self.write)

        serial_read_thread = Thread(target=self.read)
        serial_read_thread.start()

        # waiting to connect Serial Port
        time.sleep(2)
        self.__adaptor.write(bytes([0x00]))

        
    def read(self):
        while True:
            data = self.__adaptor.read(2)
            
            if len(data) < 2:
                continue
            
            # device register
            if data[0] == 0x00:
                NotificationCenter().post(
                    name=NotificationDefaultNames.REGISTER,
                    user_info={
                        'id': data[1]
                    }
                )
            # data receive
            else:
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

    def request_devices(self) -> None:
        self.__adaptor.write(bytes([0x00, 0x00]))

    def shutdown(self) -> None:
        self.__adaptor.close()
        print('serial closed.')