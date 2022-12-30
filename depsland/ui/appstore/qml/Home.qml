import QtQuick
import LKWidgets

LKWindow {
    title: 'Depsland Appstore'
    width: 400
    height: 240

    LKColumn {
        anchors {
            fill: parent
            margins: 24
        }
        alignment: 'hfill'
        spacing: 8

        LKInput {
            id: _input
            height: 24
            showClearButton: true
        }

        LKButton {
            id: _btn
            height: 24
            text: 'Install'
        }

        LKText {
            id: _msg
            height: 20
        }
    }

    Component.onCompleted: {
        py.home.init_view(
            _input,
            _btn,
            _msg,
        )
    }
}
