import QtQuick
import QtQuick.Controls
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
            color: pycolor.panel_bg
            border.width: 1
            border.color: pycolor.frame_border

            SwipeView {
                anchors {
                    top: parent.top
                    bottom: _bottom_buttons.top
                    left: parent.left
                    right: parent.right
                    margins: 2
                    bottomMargin: 8
                }
                clip: true
                interactive: false

                Page1 {}
                Page2 {}
                Page3 {}

                Component.onCompleted: {
                    py.setup_wizard.page_changed.connect((page) => {
                        this.currentIndex = page
                    })
                }
            }

            // prev & next buttons
            Item {
                id: _bottom_buttons
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                    margins: 24
                    bottomMargin: 16
                }
                height: childrenRect.height
                z: 1

                LKButton {
                    id: prev_btn
                    enabled: false
                    anchors { left: parent.left }
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
                    anchors { right: parent.right }
                    width: 100
                    bgColor: pycolor.button_bg
                    bgColorHovered: pycolor.button_bg_hovered
                    bgColorPressed: pycolor.button_bg_pressed
                    border.color: pycolor.button_border
                    text: 'Next'
                    textColor: pycolor.text_main
                }

                Component.onCompleted: {
                    py.setup_wizard.init_navigation(prev_btn, next_btn)
                }
            }
        }
    }
}
