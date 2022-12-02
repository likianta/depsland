import QtQuick
import QtQuick.Layouts
import LKWidgets

LKWindow {
    id: root
    title: 'Depsland Setup'
    width: 800
    height: 600
    color: pycolor.win_bg

    ColumnLayout {
        id: main_column
        anchors {
            fill: parent
            margins: 24
        }

        LKItem {
            id: caption
            Layout.fillWidth: true
            Layout.preferredHeight: 72

            LKText {
                anchors {
                    left: parent.left
                    verticalCenter: parent.verticalCenter
                    margins: 16
                }
                font.bold: true
                font.pixelSize: 56
                color: pycolor.text_title
                text: 'Welcome to Depsland'
            }
        }

        LKItem {
            id: subtitle
            Layout.fillWidth: true
            Layout.preferredHeight: childrenRect.height

            LKText {
                anchors {
                    left: parent.left
                    verticalCenter: parent.verticalCenter
                    margins: 16
                }
                color: pycolor.text_subtitle
                font.pixelSize: 20
                text: 'Depsland is a fundamental facility to manage your ' +
                      'Python applications.'
            }
        }

        LKRectangle {
            id: main_zone
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.topMargin: 24
            Layout.bottomMargin: 12
            color: root.color
            border.width: 1
            border.color: pycolor.frame_border

            Item {
                id: ref_point
                anchors.centerIn: parent
            }

            // the first scene
            ColumnLayout {
                anchors {
                    left: parent.left
                    right: parent.right
//                    verticalCenter: parent.verticalCenter
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
                        id: install_path
                        Layout.fillWidth: true
                        bgColor: pycolor.input_bg
                        bgColorActive: pycolor.input_bg_active
                        borderColor: pycolor.input_border
                        borderColorActive: pycolor.input_border
                        cursorColor: pycolor.input_cursor
                        textColor: pycolor.text_main
                        Component.onCompleted: {
                            this.text = py.setup_wizard.get_install_path()
                        }
                    }

                    LKButton {
                        id: browse_btn
                        Layout.preferredWidth: 100
//                        Layout.fillHeight: true
                        bgColor: pycolor.button_bg
                        bgColorHovered: pycolor.button_bg_hovered
                        bgColorPressed: pycolor.button_bg_pressed
                        border.color: pycolor.button_border
                        text: 'Browse'
                        textColor: pycolor.text_main
                    }
                }
            }

            // prev & next buttons
            Item {
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                    margins: 24
                    bottomMargin: 16
                }
                height: childrenRect.height

                LKButton {
                    id: prev_btn
                    anchors {
                        left: parent.left
//                        verticalCenter: parent.verticalCenter
                    }
                    width: 100
                    bgColor: pycolor.button_bg
                    bgColorHovered: pycolor.button_bg_hovered
                    bgColorPressed: pycolor.button_bg_pressed
                    border.color: pycolor.button_border
                    text: 'Prev'
                    textColor: pycolor.text_main
                }

                LKButton {
                    id: next_btn
                    anchors {
                        right: parent.right
//                        verticalCenter: parent.verticalCenter
                    }
                    width: 100
                    bgColor: pycolor.button_bg
                    bgColorHovered: pycolor.button_bg_hovered
                    bgColorPressed: pycolor.button_bg_pressed
                    border.color: pycolor.button_border
                    text: 'Next'
                    textColor: pycolor.text_main
                }
            }
        }
    }
}
