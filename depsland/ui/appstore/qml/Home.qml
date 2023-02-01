import QtQml
import QtQuick
import LKWidgets
import LKWidgets.Integrated

LKWindow {
    title: 'Depsland Appstore'
    width: 400
    height: 24 + _main_column.height + 24
//    height: childrenRect.height

    Behavior on height {
        id: _root_height_anim
        enabled: false
        NumberAnimation {
            duration: 400
        }
    }

    LKColumn {
        id: _main_column
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
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

        LKButton {
            id: _btn
            height: 24
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
                    running: false
                }

                Component.onCompleted: {
                    // test
                    _btn.clicked.connect(() => {
                        _refresh_anim.running = !_refresh_anim.running
                    })
                }
            }
        }

        LKText {
            id: _msg
            height: text ? 20 : 0
        }

        Component.onCompleted: {
            // when main column is ready (size is known), we can enable root
            // height animation.
            _root_height_anim.enabled = true
        }
    }

    Component.onCompleted: {
        py.home.init_view(_input, _btn, _msg)
    }
}
