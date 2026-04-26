from maya import cmds

try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore


def group_by(main_list: list, size: int = 2) -> list:
    """This function returns a list with nested lists by length of param 'size'."""
    return [main_list[i:i + size] for i in range(0, len(main_list), size)]


class MirrorSDK(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.left_side = "left"
        self.right_side = "right"
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Mirror SDK")
        self.create_layout()
        self.connect_buttons()
        self.setMinimumWidth(230)
        self.show()

    def create_layout(self):
        ql_left = QtWidgets.QLabel("Left")
        self.qle_left = QtWidgets.QLineEdit(self.left_side)
        ql_right = QtWidgets.QLabel("Right")
        self.qle_right = QtWidgets.QLineEdit(self.right_side)
        self.qpb_mirror = QtWidgets.QPushButton("Mirror SDK")
        qvl_layout = QtWidgets.QVBoxLayout()
        qhl_layout1 = QtWidgets.QHBoxLayout()
        qhl_layout2 = QtWidgets.QHBoxLayout()
        qhl_layout1.addWidget(ql_left)
        qhl_layout1.addWidget(self.qle_left)
        qhl_layout2.addWidget(ql_right)
        qhl_layout2.addWidget(self.qle_right)
        qvl_layout.addLayout(qhl_layout1)
        qvl_layout.addLayout(qhl_layout2)
        qvl_layout.addWidget(self.qpb_mirror)
        self.setLayout(qvl_layout)

    def connect_buttons(self):
        self.qpb_mirror.clicked.connect(self.mirror)

    def mirror(self):
        self.left_side = self.qle_left.text()
        self.right_side = self.qle_right.text()
        sel = cmds.ls(sl=True)
        attrs = cmds.channelBox("mainChannelBox", q=True, sma=True)
        if sel and attrs:
            for obj in sel:
                for attr in attrs:
                    self.iter_nodes(f"{obj}.{attr}")
        else:
            cmds.warning("Please select a control and one or more attribute")

    def get_or_duplicate(self, name: str) -> str:
        """Return a mirrored or duplicated node."""
        if cmds.ls(name, type="transform"):
            return name.replace(self.left_side, self.right_side, 1)
        existing = cmds.ls(name + "_copy")
        if existing:
            return existing[0]
        return cmds.duplicate(name, name=name + "_copy")[0]

    def iter_nodes(self, src):
        """Recursively copy and reconnect attribute pairs."""
        connections = cmds.listConnections(src, plugs=True, source=False, destination=True, connections=True) or []
        for a, b in group_by(connections, 2):
            aName, aAttr = a.split(".")
            bName, bAttr = b.split(".")
            aCopy = self.get_or_duplicate(aName)
            bCopy = self.get_or_duplicate(bName)
            cmds.connectAttr(f"{aCopy}.{aAttr}", f"{bCopy}.{bAttr}", force=True)
            if not cmds.ls(bName, type="transform"):
                self.iter_nodes(bName)

tool = MirrorSDK()
