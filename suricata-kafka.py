#!/usr/local/bin/python
# Reverse compatibility stuffs
from __future__ import absolute_import, division, print_function
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                       int, map, next, oct, open, pow, range, round,
                       str, super, zip)
from kafka import KafkaProducer

import threading
import argparse
import multiprocessing
import os
import sys
import socket
import logging
import traceback
import time


def set_logging(log_level):
    # Set logging level. Log to directory script was run from as __file__.stderr
    logging_level = getattr(logging, log_level.upper())
    # TODO Put script log in a better place
    log_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
    # Set basic logging configuration
    logging.basicConfig(filename='{dir}/{file}.stderr'.format(
        dir=log_dir,
        file=log_file,
        level=logging_level,
        format='%(asctime)s %(levelname)-8s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout))
    # add info level meessage to log to show start of process
    logging.info('Logging to {dir}/{file}'.format(dir=log_dir, file=log_file))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log-level', type=str, help='DEBUG|INFO|WARNING|ERROR|CRITICAL', default="INFO",
                        choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG'])
    parser.add_argument('-s', '--socket', help='Full path to write the unix socket',
                        default="/var/lib/suricata/eve.sock")
    parser.add_argument('-b', '--buffer', type=int, help='Set buffer size for eve messages', default=4096,
                        choices=range(0, 65535))
    parser.add_argument('-k', '--bootstrap-servers', nargs='+', help='List of Kafka brokers',
                        default=['localhost:9092'])
    parser.add_argument('-t', '--topic', type=str, help='Topic to send suricata alerts to', default='suricata-raw')

    args = parser.parse_args()

    # Sanity check the bootstrap servers to see if a port was provided
    if args.bootstrap_servers:
        # iterate through the list of servers and add default ports if missing
        for count, item in enumerate(args.bootstrap_servers):
            # split results into list of IP PORT
            result = item.split(':')
            # If port is missing add default listen port
            if len(result) == 1:
                args.bootstrap_servers[count] = "{}{}".format(item, ":9092")

    return args


def create_socket(path):
    server_address = path
    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Bind the socket to the file
    logging.info('Starting unix stream socket located at {}'.format(path))
    sock.bind(server_address)
    return sock


def linesplit(socket):
    buffer = socket.recv(4096)
    buffering = True
    while buffering:
        if "\n" in buffer:
            (line, buffer) = buffer.split("\n", 1)
            yield line
        else:
            more = socket.recv(4096)
            if not more:
                buffering = False
            else:
                buffer += more
    if buffer:
        yield buffer


def send_data(boot_servers):
    producer = KafkaProducer(bootstrap_server=boot_servers)

def read_data(sock, buffer, topic, boot_servers):
    # Listen for incoming connections
    sock.listen(1)
    logging.info('Socket ready for incoming connections')

    # Wait for a connection
    logging.info('Waiting for a connection')
    connection, client_address = sock.accept()
    producer = KafkaProducer(bootstrap_servers=boot_servers)
    while True:
        try:
            logging.info('Connection from {}'.format(client_address))
            # Receive the data in chunks based on buffer
            # Buffer size should be large enough to get a full eve alert in a single data chunk
            while True:
                # TODO Read from the buffer
                data = linesplit(connection)
                try:
                    producer.send(topic=topic, value=next(data))
                except StopIteration:
                    # no data left to read
                    break
        finally:
            # Clean up the connection
            connection.close()
    

def run():
    """
    get arguments, arguments are added as a dict using the long list option as
    the name. Any long list item with a - in the name will be stored as _ for
    example log-level would be accessed vi args.log_level.
    """
    args = get_args()
    print(args)

    # Set the logging level based on the config
    set_logging(args.log_level)

    # make sure we are working in the directory of the python executable
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create the socket and Begin Reading data
    read_data(create_socket(args.socket), args.buffer, args.topic, args.bootstrap_servers)


if __name__ == '__main__':
    run()
