import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QmlEase

Window {
    id: root
    title: 'Depsland AppBuilder'
    width: 800
    height: 1400

    property string appName
    property string appVersion
    property string projectDir

    signal projectPathSubmit(string path)

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
            id: _project_dir_input
            // Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            label: 'Please input your project directory'
            text: root.projectDir
            // outlineColor: pycolor.primary
//            onEditingFinished: (text) => {
//                console.log('editing finished', text)
//            }
            Component.onCompleted: {
                this.editingFinished.connect(root.projectPathSubmit)
            }
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
                id: _app_name_input
                // Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
                label: 'AppName'
                text: root.appName
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
                text: root.appVersion
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

    Component.onCompleted: {
        py.main.init_ui(this)
    }
}
