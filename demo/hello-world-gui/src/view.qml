import QtQuick
import LKWidgets

LKWindow {
    title: 'Hello World'

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
