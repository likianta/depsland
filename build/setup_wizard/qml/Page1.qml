import QtQuick
import QtQuick.Layouts
import LKWidgets

Item {
    id: root

    Item {
        id: ref_point
        anchors.centerIn: parent
    }

    ColumnLayout {
        anchors {
            left: parent.left
            right: parent.right
            margins: 24
        }
        y: ref_point.y - 90
        height: childrenRect.height

        LKItem {
            Layout.fillWidth: true
            Layout.preferredHeight: childrenRect.height
            LKText {
                anchors {
                    left: parent.left
                    verticalCenter: parent.verticalCenter
                }
                color: pycolor.text_main
                font.pixelSize: 14
                text: 'Choose a location to install depsland'
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: childrenRect.height
            Layout.topMargin: 8

            LKInput {
                id: _install_path
                Layout.fillWidth: true
                bgColor: pycolor.input_bg
                bgColorActive: pycolor.input_bg_active
                borderColor: pycolor.input_border
                borderColorActive: pycolor.input_border
                textColor: pycolor.text_main
                inputItem.selectionColor: pycolor.input_selection
                Component.onCompleted: {
                    py.page1.init_input_bar(this)
                    this.text = py.page1.get_install_path()
                }
            }

            LKButton {
                id: _browse_btn
                Layout.preferredWidth: 100
                bgColor: pycolor.button_bg
                bgColorHovered: pycolor.button_bg_hovered
                bgColorPressed: pycolor.button_bg_pressed
                border.color: pycolor.button_border
                text: 'Browse'
                textColor: pycolor.text_main

                property bool _firstTimeOpen: true

                onClicked: {
                    if (this._firstTimeOpen) {
                        const path = lkutil.file_dialog(
                            'open', 'folder', _install_path.text
                        )
                        if (path) {
                            this._firstTimeOpen = false
                            console.log('path: ' + path)
                            _install_path.text = path
                        }
                    } else {
                        const path = lkutil.file_dialog(
                            'open', 'folder',
                        )
                        if (path) {
                            console.log('path: ' + path)
                            _install_path.text = path
                        }
                    }
                }
            }
        }
    }
}
