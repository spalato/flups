import sys
import os.path as pth
import logging
from PySide6 import QtWidgets
from flups.pigui.pigui import PIWidget, PiguiAppData, PiguiController

# TODO: add a default "safe mode" in case of bugs at launch due to errors in pigui.toml
def launch_pigui():
    logging.basicConfig(level=logging.DEBUG)
    cfg_file = pth.join(
        pth.dirname(__file__),
        "pigui.toml"
    )
    default_cfg = dict(port="Mock", axis="0", autoconnect=True)
    if pth.exists(cfg_file):
        logging.info(f"Loading config from: {cfg_file}")
        try:
            appdata = PiguiAppData.from_toml(cfg_file)
        except TypeError:
            logging.warning(f"Loading config failed. Resorting to default.")
            appdata = PiguiAppData(**default_cfg)  #
    else:
        appdata = PiguiAppData(**default_cfg)  #

    app = QtWidgets.QApplication([])
    ctrl = PiguiController(appdata)
    piguiw = PIWidget(appdata, ctrl)
    ctrl.moveDone.connect(app.beep)
    piguiw.show()
    ret = app.exec()
    logging.info(f"Saving config to: {cfg_file}")
    appdata.to_toml(cfg_file)
    return ret


if __name__ == "__main__":
    sys.exit(launch_pigui())
