import QtQuick
import QtQuick.Layouts
import QmlEase
import QmlEase.Composites
import QmlEase.Layouts

Container {
    border.width: 1
    padding: 8

    property alias model: _source.model

    Vertical {
        anchors.fill: parent

        SwipeView {
            id: _swipeView
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            TreeView {
                id: _source
                checkable: true
                expandRoot: true
            }
            
            TreeView {
                id: _target
                checkable: false
                expandRoot: true
                Component.onCompleted: {
                    _source.nodeChecked.connect(() => {
                        _target.model = _source.extractCheckedTree()
                    })
                }
            }
        }

        Button {
            Layout.fillWidth: true
            text: _swipeView.currentIndex == 0 ? 'Preview output tree' : 'Back'
            onClicked: {
                _swipeView.currentIndex ^= 1
            }
        }
    }
}