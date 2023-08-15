import QtQuick
import LKWidgets

LKWindow {
    LKRectangle {
        anchors {
            fill: parent
            margins: 24
        }
        LKText {
            anchors.centerIn: parent
            text: 'Hello World'
        }
    }
}