import QtQuick
import QtQuick.Layouts
import QmlEase
import QmlEase.Layouts

Window {
    id: root
    title: 'Depsland AppBuilder'
    width: 800
    height: 1400

    property alias  appId: _appidInput.text
    property alias  appName: _app_name_input.text
    property alias  appVersion: _app_version_input.text
    property alias  assetsModel: _assets.model
    // property alias assetsSourceModel: _assetsTree.model
    // property alias assetsTargetModel: _assetsTreePreview.model
    property alias  projectDir: _projectDirInput.text
    property string venvPath

    // signal assetsTreeNodeChanged()
    signal onBumpVersion()
    signal onRegenerateId()
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
            leftMargin: 80
            right: parent.right
            rightMargin: 80
            // bottomMargin: 48
        }
        spacing: 12

        TextInput {
            id: _projectDirInput
            // Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            label: 'Please input your project directory'
            // outlineColor: pycolor.primary
            showEditingHint: true
            text: root.projectDir
            Component.onCompleted: {
                this.editingFinished.connect(root.projectPathSubmit)
            }
        }
        
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            spacing: 12

            TextInput {
                id: _appidInput
                // Layout.alignment: Qt.AlignVCenter
                Layout.fillWidth: true
                enabled: false
                label: 'AppID'
                // text: root.appId
            }

            Button {
                Layout.alignment: Qt.AlignBottom
                Layout.preferredWidth: 160
                text: 'Regenerate ID'
                onClicked: root.onRegenerateId()
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
                // text: root.appName
            }

            Empty {
                Layout.fillHeight: true
                Layout.preferredWidth: 160
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            spacing: 12

            TextInput {
                id: _app_version_input
                Layout.fillWidth: true
                label: 'Version'
                // text: root.appVersion
            }

            RadioGroup {
                Layout.fillWidth: true
                horizontal: true
                index: 2
                label: 'Switch version'
                model: ['Alpha', 'Beta', 'Formal']
            }

            Button {
                id: _bumpVersionButton
                Layout.alignment: Qt.AlignBottom
                Layout.preferredWidth: 160
                // text: 'Elevate version number'
                text: 'Bump version'
                onClicked: root.onBumpVersion()
            }
            // Component.onCompleted: {
            //     py.qmlease.inspect_size(_bumpVersionButton)
            // }
        }

        TabsLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 1000
            model: ['Assets', 'Dependencies', 'Encryption']
            
            AssetsPicker { id: _assets }
            Dependencies {
                id: _deps
                venvPath: root.venvPath
            }
            Container { 
                border.width: 1
                padding: 8
            }
        }
    }

    Component.onCompleted: {
        py.main.init_ui(this)
    }
}
