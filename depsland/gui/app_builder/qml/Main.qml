import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QmlEase
// import MD3

Window {
    title: 'Depsland AppBuilder'
    width: 800
    height: 1400

    ColumnLayout {
        anchors {
            // fill: parent
            // top: parent.top
            // horizontalCenter: parent.horizontalCenter
            // margins: 24
            top: parent.top
            topMargin: 48
            left: parent.left
            leftMargin: 120
            right: parent.right
            rightMargin: 120
            // bottomMargin: 48
        }
        spacing: 12

        TextInput {
            // Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            label: 'Please input your project directory'
            // outlineColor: pycolor.primary
        }
        
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            spacing: 12

            TextInput {
                // Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
                enabled: false
                label: 'AppID'
            }

            Button {
                Layout.alignment: Qt.AlignBottom
                width: 160
                text: 'Regenerate ID'
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            spacing: 12

            TextInput {
                // Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
                label: 'AppName'
            }

            Empty {
                Layout.fillHeight: true
                width: 160
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            spacing: 12

            TextInput {
                Layout.fillWidth: true
                label: 'Version'
            }

            RadioGroup {
                Layout.fillWidth: true
                label: 'Switch version'
                model: ['Alpha', 'Beta', 'Formal']
            }

            Button {
                Layout.alignment: Qt.AlignBottom
                width: 160
                // text: 'Elevate version number'
                text: 'Bump version'
            }
        }
    }
}
