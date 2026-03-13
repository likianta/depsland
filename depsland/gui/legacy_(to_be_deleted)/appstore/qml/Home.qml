import QtQml
import QtQuick
import LKWidgets

LKWindow {
    id: root
    title: 'Depsland Appstore ' + py.home.get_app_version()
    width: 400
    height: 24 + _main_column.height + 24
//    height: childrenRect.height

    LKColumn {
        id: _main_column
        anchors {
            left: parent.left
            right: parent.right
            verticalCenter: parent.verticalCenter
            margins: 24
        }
        height: childrenRect.height
        alignment: 'hfill'
        spacing: 8

        LKInput {
            id: _input
            height: 24
            showClearButton: true
        }

        Item {
            id: _buttons
            height: 24

            LKButton {
                id: _stop_btn
                anchors {
                    right: parent.right
                    top: parent.top
                    bottom: parent.bottom
                }
                width: 0
                text: 'Stop'

                Behavior on width {
                    NumberAnimation {
                        duration: 100
                    }
                }
            }

            LKButton {
                id: _install_btn
                anchors {
                    left: parent.left
                    right: _stop_btn.left
                    top: parent.top
                    bottom: parent.bottom
                    rightMargin: _stop_btn.width > 0 ? 8 : 0
                }
                text: 'Install'

                LKIcon {
                    id: _refresh_icon
                    anchors {
                        left: parent.left
                        verticalCenter: parent.verticalCenter
                        leftMargin: 12
                    }
                    opacity: _refresh_anim.running ? 1 : 0
                    size: 14
                    source: pyassets.src('refresh-line.svg')
    //                color: pycolor.text_hint

                    Behavior on opacity {
                        NumberAnimation {
                            duration: 500
                        }
                    }

                    RotationAnimator on rotation {
                        id: _refresh_anim
                        alwaysRunToEnd: true
                        from: 0
                        to: 360
                        duration: 1000
                        loops: Animation.Infinite
                        running: _install_btn.text == 'Installing...'
                    }

//                    Component.onCompleted: {
//                        _install_btn.clicked.connect(() => {
//                            _refresh_anim.running = !_refresh_anim.running
//                        })
//                    }
                }
            }
        }

        LKText {
            id: _info
            leftPadding: 4
            color: pycolor.text_secondary
        }
    }

    LKFileDrop {
        id: _drop_area
        anchors { fill: parent }
    }

    Component.onCompleted: {
        py.home.init_view(
            _input, _install_btn, _stop_btn, _info, _drop_area
        )
    }
}
