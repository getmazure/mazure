import argparse
import logging
import signal
import sys
from http.server import ThreadingHTTPServer
from typing import Any

from mazure.mazure_proxy import logger
from mazure.mazure_proxy.proxy3 import CertificateCreator, ProxyRequestHandler


def signal_handler(signum: Any, frame: Any) -> None:  # pylint: disable=unused-argument
    sys.exit(0)


def get_help_msg() -> str:
    msg = """
    ##################################################
    @      @    @@    @@@@@@@ @      @  @@@@@@  @@@@@@
    @@    @@   @  @       @   @      @  @    @  @       
    @@@  @@@  @    @     @    @      @  @@@@@@  @@@@@@
    @  @@  @ @@@@@@@@   @     @      @  @@      @       
    @      @ @      @  @      @      @  @ @@    @       
    @      @ @      @ @@@@@@@ @@@@@@@@  @   @@  @@@@@@
    ##################################################"""
    msg += "\n\n"
    msg += f"\texport REQUESTS_CA_BUNDLE={CertificateCreator.cacert}"
    msg += "\n\n"
    msg += "\tHTTPS_PROXY=http://localhost:5005 pytest tests_dir\n"
    msg += "\n"
    msg += "\tHTTPS_PROXY=http://localhost:5005 mvn test\n"
    msg += "\n"
    msg += "\tHTTPS_PROXY=http://localhost:5005 dotnet test MyProject\n"
    return msg


def main(argv: Any = None) -> None:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=get_help_msg()
    )

    parser.add_argument(
        "-H", "--host", type=str, help="Which host to bind", default="127.0.0.1"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        help="Port number to use for connection",
        default=5005,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Add verbose logging",
    )

    args = parser.parse_args(argv)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    ProxyRequestHandler.validate()

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except ValueError:
        pass  # ignore "ValueError: signal only works in main thread"

    server_address = (args.host, args.port)

    httpd = ThreadingHTTPServer(server_address, ProxyRequestHandler)

    sa = httpd.socket.getsockname()

    print("Call `mazure -h` for example invocations")
    print(f"Serving HTTP Proxy on {sa[0]}:{sa[1]} ...")  # noqa
    httpd.serve_forever()


if __name__ == "__main__":
    main()
