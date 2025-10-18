
import logging
from PySide2.QtWidgets import (QWidget, QPushButton, QSpinBox, QLabel, QFrame, 
    QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox)
from PySide2.QtCore import Qt, QSize

# from qtlets.qtlets import HasQtlets
from qtlets.widgets import IntEdit, FloatEdit
logger = logging.getLogger()

class PIStage_Control(QWidget):
    def __init__(self, *args, stage=None, **kwargs):
        super().__init__(*args, **kwargs)

        #self.com_port_edit = QLineEdit() # or dropdown?
        #self.stage_number = QLineEdit() # or dropdown?

        self.current_pos = IntEdit(0)
        self.current_pos.setDisabled(True)
        self.pos_edit = IntEdit(0)
        #self.pos_edit.setRange(-2**16, 2**16)
        self.velocity_edit = QSpinBox()
        self.velocity_edit.setRange(1, 200_000)
        self.velocity_edit.setStepType(QSpinBox.AdaptiveDecimalStepType)
        self.go_min_btn = QPushButton("<")
        self.stop_btn = QPushButton("X")
        self.go_max_btn = QPushButton(">")
        self.moving_label = QLabel()
        self.moving_label.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.moving_label.setText("Moving?")
        self.moving_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        for btn in (self.go_min_btn, self.go_max_btn, self.stop_btn):
            btn.setMinimumWidth(24)
            btn.setStyleSheet("QPushButton {text-align: center;}")

        self.setLayout(QGridLayout())
        #self.setLayout(QVBoxLayout())
        
        # Instrument config
        # config_box = QGroupBox("Stage config")
        # self.layout().addWidget(config_box)
        
        # config_box.setLayout(QVBoxLayout())
        # config_box.addWidget(self.com_port_edit)
        # config_box.addWidget(self.stage_number)

        self.layout().addWidget(QLabel("Current"), 0, 0)
        self.layout().addWidget(self.current_pos, 0, 1)
        self.layout().addWidget(QLabel("Target"), 1, 0)
        self.layout().addWidget(self.pos_edit, 1, 1)
        self.layout().addWidget(QLabel("Velocity"), 2, 0)
        self.layout().addWidget(self.velocity_edit, 2, 1)
        self.layout().addWidget(QLabel("Status"), 3, 0)
        self.layout().addWidget(self.moving_label, 3, 1)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.go_min_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.go_max_btn)
        self.layout().addLayout(btn_layout, 4, 0, 1, 2)
        if stage is not None:
            self.link_stage(stage)


    def link_stage(self, stage):
        logger.debug("Linking to %s", repr(stage))
        self.pos_edit.valueEdited.connect(stage.move_to)
        stage.link_widget(self.velocity_edit, "velocity")
        stage.link_widget(
            self.current_pos, "pos",
        ).use_polling()

        self.go_min_btn.clicked.connect(stage.find_min_edge)
        self.stop_btn.clicked.connect(stage.stop)
        self.go_max_btn.clicked.connect(stage.find_max_edge)


    def sizeHint(self):
        return QSize(160, 120)



        






