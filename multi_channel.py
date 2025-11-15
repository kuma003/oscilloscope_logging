import sys
import time
import csv
import pyvisa

from dataclasses import dataclass


@dataclass
class ChannelConfig:
    total_points: float
    xinc: float
    ymult: float
    yorig: float
    yref: float

    def to_voltage(self, raw):
        voltages = [((d - self.yref) - self.yorig) * self.ymult for d in raw]
        return voltages


FILE_PATH = "data.csv"
CHANNELS = [1, 2]
rm = pyvisa.ResourceManager()
visaList = rm.list_resources()
RESOURCE = visaList[0]  # or specify your disired

wn_channels = len(CHANNELS)
ch_cfgs = []

with open(FILE_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    header = ["Time [s]"] + [f"Channel {ch} Voltage [V]" for ch in CHANNELS]
    writer.writerow(header)

    osillo = rm.open_resource(RESOURCE)
    osillo.timeout = 5000  # 5 seconds for timeout

    # initialize each channel
    for ch in CHANNELS:
        osillo.write(f":WAVeform:SOURce CHAN{ch}")
        osillo.write(":WAVeform:MODE NORMal")
        osillo.write(":WAVeform:FORMat BYTE")
        osillo.write(":WAVeform:ENCdg RIBinary")
        osillo.write(":WAVeform:DATA:WIDth 1")

        pre = osillo.query(":WAVeform:PREamble?").split(",")
        cfg = ChannelConfig(
            total_points=int(pre[2]),
            xinc=float(pre[4]),
            ymult=float(pre[7]),
            yorig=float(pre[8]),
            yref=float(pre[9]),
        )
        ch_cfgs.append(cfg)

    start_time = time.time()

    while True:
        row = [time.time() - start_time]
        for ch, cfg in zip(CHANNELS, ch_cfgs):
            # set channel
            osillo.write(f":WAVeform:SOURce CHAN{ch}")
            raw = osillo.query_binary_values(
                ":WAVeform:DATA?", datatype="B", container=list, header_fmt="ieee"
            )

            volts = cfg.to_voltage(raw)
            v_avg = sum(volts) / len(volts)
            row.append(v_avg)

        writer.writerow(row)
