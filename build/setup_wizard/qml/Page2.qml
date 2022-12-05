import QtQuick
import QtQuick.Layouts
import LKWidgets
import LKWidgets.Progress

LKItem {
    id: root

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24

//        LKText {
//            Layout.fillWidth: true
//            Layout.preferredHeight: childrenRect.height
//            text: 'In Progress'
//        }

        LKListView {
            id: listview
            Layout.fillWidth: true
            Layout.fillHeight: true
//            highlightFollowsCurrentItem: false
            model: py.page2.get_model()
            spacing: 8

            delegate: LKRectangle {
                id: _row_item
                width: listview.width
                height: 48
                radius: 6
                border.width: _focused ? 1 : 0
                border.color: pycolor.border_highlighted
                color: pycolor.progress_bg

                property bool _focused: model.index == listview.currentIndex

                RowLayout {
                    anchors {
                        fill: parent
                        topMargin: 4
                        bottomMargin: 4
                        leftMargin: 12
                        rightMargin: 12
                    }

                    Item {
                        Layout.preferredWidth: childrenRect.width
                        Layout.fillHeight: true

                        LKCircleProgress {
                            id: _prog
                            anchors {
                                verticalCenter: parent.verticalCenter
                            }
                            animateValueDuration: 50
                            circleSize: 32
                            color0: _row_item.color
                            color1: pycolor.progress_fg_dimmed
                            color2: pycolor.progress_fg
                            ringSize: 3
                            value: model.progress / 100
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.leftMargin: 12
                        Layout.rightMargin: 12

                        LKText {
                            id: _main_name
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            text: model.name
                        }

                        LKText {
                            id: _processing_info
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: pycolor.text_dimmed
                            font.pixelSize: 10
                            horizontalAlignment: Text.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                            text: model.processing
                        }
                    }
                }
            }

            Component.onCompleted: {
                py.page2.index_changed.connect((idx) => {
                    this.currentIndex = idx
//                    this.positionViewAtIndex(idx, ListView.Contain)
                })
            }
        }
    }
}

