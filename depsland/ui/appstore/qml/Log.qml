import QtQuick
import LKWidgets
import LKWidgets.Functional

LKLogPanel {
    id: _log
//        visible: Boolean(_log.count)
    anchors {
        left: parent.left
        right: parent.right
        top: _main_column.bottom
//            bottom: parent.bottom
        leftMargin: 24
        rightMargin: 24
        topMargin: 8
//            bottomMargin: 8
    }
    height: Boolean(_log.count) ? 240 : 0
    opacity: Boolean(_log.count) ? 1 : 0

    Behavior on height {
        NumberAnimation {
            duration: 500
//                easing.type: Easing.OutQuad
        }
    }

    Behavior on opacity {
        NumberAnimation {
            duration: 500
        }
    }
}
