"""An asynchronous Python client for controlling SBB devices."""

__all__ = "SBBClient"


from asyncio import (
    Semaphore,
    StreamReader,
    StreamWriter,
    TimeoutError,
    open_connection,
    sleep,
    wait_for,
)
from dataclasses import dataclass, field
from logging import getLogger
from typing import Any, Callable, Optional, Tuple, Union

from .patterns import ipv4_pattern
from .validations import Validations

log = getLogger()

init_commands = ("configure echoCommands 1", "detatchController")


@dataclass
class SBBClient(Validations):
    """Asynchronous sys-botbase client/server framework in Python.

    Attributes:
    ip: The IP address of the sys-botbase device.
    port: The port number of the sys-botbase device.
    timeout: The timeout in seconds for all asynchronous operations.
    verbose: Whether to log debug information.
    semaphore: A semaphore to ensure that only one transaction can be active at a time.
    connected: Whether the client is currently connected to the sys-botbase device.
    reader: A StreamReader object for reading data from the sys-botbase device.
    writer: A StreamWriter object for writing data to the sys-botbase device.
    log: A function to log debug information.

    Methods:
    __call__(*args): Send the specified commands to the sys-botbase device and return the responses.
    """

    ip: str
    port: int = 6000
    timeout: float = 1.0
    verbose: bool = False
    semaphore: Semaphore = field(init=False)
    connected: bool = field(init=False)
    reader: StreamReader = field(init=False)
    writer: StreamWriter = field(init=False)
    log: Callable = field(init=False)

    @staticmethod
    def _validate_ip(ip: str, **_: object) -> Optional[str]:
        """Validate the IP address of the sys-botbase device.

    Args:
        ip: The IP address to validate.

    Returns:
        The IP address, if it is valid.
        None, if the IP address is invalid.

    Raises:
        ValueError: If the IP address is invalid.
        """
        if ipv4_pattern.match(ip):
            return ip
        else:
            raise ValueError("[X] The IP address is invalid.")

    def __post_init__(self) -> None:
        """Initialize the SBBClient."""
        super().__post_init__()
        self.semaphore = Semaphore(1)
        self.connected = False
        self.reader, self.writer = [None] * 2
        if self.verbose:
            self.log = log.info
        else:
            self.log = log.debug
            #init_commands = init_commands + ("configure printDebugResultCodes 1",)


    async def _connect(self) -> None:
        """Connect to the sys-botbase device."""
        self.reader, self.writer = await open_connection(
            self.ip, self.port, limit=(1024 * 1024)
        )
        self.connected = True

    async def __call__(self, *args) -> Union[Tuple[Any, ...], bool, Any]:
        """Send the specified commands to the sys-botbase device and return the responses.

    Args:
        *args: The commands to send to the sys-botbase device.

    Returns:
        A tuple of the responses from the sys-botbase device, if there are multiple responses.
        A single response from the sys-botbase device, if there is only one response.
        True, if there are no responses from the sys-botbase device.
    Raises:
        TimeoutError
        """
        res = []
        try:
            if not self.connected:
                self.log(f"[...] Attempting to connecting to {self.ip}")
                await wait_for(self._connect(), self.timeout)
                self.log(f"[...] Setting up connection to {self.ip}")
                await wait_for(self(*init_commands), self.timeout)
                self.log(f"[✓] Successfully connected to {self.ip}")
            await self.semaphore.acquire()
            self.log("[...] Waiting for commands")
            for command in args:
                self.log(f"[>>>] Sending {command}")
                command += "\r\n"
                self.writer.write(command.encode())
                await wait_for(self.writer.drain(), self.timeout)
                while True:
                    r = await wait_for(self.reader.readline(), self.timeout)
                    if r == command.encode():
                        self.log("[<<<] Received command echo")
                        if "Seq" in command:
                            self.log("[...] Waiting for Sequence to finish")
                            continue
                        break
                    else:
                        response = r[:-1].decode()
                        self.log(f"[<<<] Received response of len {len(response)}")
                        res.append(response)
                        if response == "done":
                            self.log("[✓] Sequence finished")
                            break
                    await sleep(0)
        except TimeoutError:
            self.connected = False
            log.error("[!] Session timed out")
        finally:
            self.semaphore.release()
            self.log(f"[✓] Transaction finished with {len(res)} responses!")
        if res:
            if len(res) == 1:
                return res[0]
            else:
                return tuple(res)
        else:
            return True

    async def disconnect(self) -> None:
        """Disconnect from the sys-botbase device."""

        if self.connected:
            self.reader.close()
            self.writer.close()
            self.connected = False
