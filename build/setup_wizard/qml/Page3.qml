import QtQuick
import QtQuick.Layouts
import LKWidgets

Item {
    id: root

    RowLayout {
        anchors {
            fill: parent
            margins: 32
        }

        LKText {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.rightMargin: 24
            textFormat: Text.MarkdownText
            Component.onCompleted: {
                this.text = py.page3.get_text()
            }
        }

        Item {
            Layout.preferredWidth: 240
            Layout.fillHeight: true
            clip: true

            Column {
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: _qrcode_animated_bg.top
                    bottomMargin: 4
                }
                clip: true
                spacing: 2

                LKText {
                    id: _name
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: pycolor.text_accent
                    font.bold: true
                    font.pixelSize: 20
                    horizontalAlignment: Text.AlignHCenter
                    text: 'LIKIANTA'
                }

                LKText {
                    id: _number
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: pycolor.text_dimmed
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    text: '3300683735'
                }
            }

            AnimatedImage {
                id: _qrcode_animated_bg
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                    bottomMargin: 4
                }
                height: width
                fillMode: Image.PreserveAspectFit
                smooth: true
                source: 'Assets/irregular-circle-anim-dark.gif'

                Image {
                    anchors.centerIn: parent
                    width: 100
                    height: width
                    source: 'Assets/qrcode.svg'
                }
            }
        }
    }

//    ColumnLayout {
//        anchors {
//            fill: parent
//            margins: 32
//        }
//
//        LKText {
//            Layout.fillWidth: true
//            Layout.fillHeight: true
//            textFormat: Text.MarkdownText
//            Component.onCompleted: {
//                this.text = py.page3.get_text()
//            }
//        }
//
//        LKRectangle {
//            Layout.fillWidth: true
//            Layout.fillHeight: true
//            border.width: 1
//            border.color: pycolor.frame_border
//            color: pycolor.panel_bg
//
//            ColumnLayout {
//                anchors {
//                    top: parent.top
//                    bottom: parent.bottom
//                    horizontalCenter: parent.horizontalCenter
//                    margins: 8
//                }
//                width: childrenRect.width
//
//                LKText {
//                    id: _name
////                    Layout.preferredWidth: childrenRect.width
////                    Layout.preferredHeight: childrenRect.height
//                    color: pycolor.text_title
//                    font.bold: true
//                    font.pixelSize: 28
//                    horizontalAlignment: Text.AlignHCenter
//                    text: 'LIKIANTA'
//                }
//
//                LKText {
//                    id: _number
////                    Layout.preferredWidth: childrenRect.width
////                    Layout.preferredHeight: childrenRect.height
//                    color: pycolor.text_subtitle
//                    font.pixelSize: 16
//                    horizontalAlignment: Text.AlignHCenter
//                    text: '3300683735'
//                }
//
//                AnimatedImage {
//                    Layout.preferredWidth: 200
////                    Layout.preferredHeight: childrenRect.height
////                    width: 200
////                    height: 200
////                    Layout.fillWidth: true
//                    Layout.fillHeight: true
//                    Layout.margins: 16
//                    fillMode: Image.PreserveAspectFit
//                    smooth: true
//                    source: 'Assets/irregular-circle-anim-dark.gif'
//
//                    Image {
//                        anchors.centerIn: parent
//                        width: 160
//                        height: 160
//                        source: 'Assets/qrcode.svg'
//                    }
//                }
//            }
//        }
//    }
}
