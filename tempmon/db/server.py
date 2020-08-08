import socket
import pickle
import os
import datetime
import signal
import select
# pylint: disable=relative-beyond-top-level
from . import ADR, DATA

class Data:
    def __init__(self):
        self.date = datetime.date.today()
        self.data = Data._load(self.date)

    def insert(self, degrees):
        # TODO: check that degrees is an int
        now = datetime.datetime.today()

        if (now.date() - self.date).days > 0:
            self.save()
            self.date = now.date()
            self.data = []

        if len(self.data) >= 2:
            if self.data[-2][1] == self.data[-1][1] == degrees:
                self.data.pop()

        seconds = 3600*now.hour + 60*now.minute + now.second
        self.data.append((seconds, degrees))

    def get(self, year, month, day):
        date = datetime.date(year, month, day)
        if date == self.date:
            return self.data
        else:
            return Data._load(date)

    @staticmethod
    def _data_filename(date):
        return os.path.join(DATA, "{:04}-{:02}-{:02}".format(date.year, date.month, date.day))

    def save(self):
        with open(Data._data_filename(self.date), "w") as f:
            for d in self.data:
                f.write("{0} {1}\n".format(*d))

    @staticmethod
    def _load(date):
        filename = Data._data_filename(date)
        data = []
        if os.path.isfile(filename):
            with open(filename, "r") as f:
                for l in f:
                    spl = l.rstrip().split(" ")
                    data.append((int(spl[0]), int(spl[1])))
        return data

def process_request(msg, d):
    op, args = msg

    if op == "put":
        d.insert(args)
        return True, ()
    elif op == "get":
        return True, d.get(*args)

    return False, "unknown opcode"

def handle_request(conn, d):
    with conn.makefile("rb") as f:
        msg = pickle.load(f)
    conn.shutdown(socket.SHUT_RD)

    answer = process_request(msg, d)

    with conn.makefile("wb") as f:
        pickle.dump(answer, f)
    conn.shutdown(socket.SHUT_WR)

def main():
    d = Data()

    running = True
    def sighandler(_signum, _asd):
        nonlocal running
        running = False
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_CLOEXEC) as serv:
        if os.path.exists(ADR):
            os.remove(ADR)
        serv.bind(ADR)
        serv.listen()

        sigr, sigw = os.pipe2(os.O_NONBLOCK)
        signal.set_wakeup_fd(sigw, warn_on_full_buffer=False)
        while running:
            rdy, _, _ = select.select([serv, sigr], [], [])
            for r in rdy:
                if r is serv:
                    conn, _ = serv.accept()
                    with conn:
                        handle_request(conn, d)
                elif r is sigr:
                    os.read(sigr, 1024)

    d.save()

if __name__ == "__main__":
    main()
