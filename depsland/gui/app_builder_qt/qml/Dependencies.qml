import QtQuick
import QtQuick.Layouts
import QmlEase

Container {
    id: root
    border.width: 1
    padding: 8

    property string venvPath  // the auto-detected venv path

    Vertical {
        width: parent.width
        spacing: 12

        RadioGroup {
            id: _radioGroup
            // Layout.fillWidth: true
            ghostBorder: true
            index: 3
            label: 'How do you want to integrate Python dependencies?'
            model: [
                'Not included',
                'Cloud hosted',
                'Directly embedded (not recommended)',
                'Compressed and embedded',
            ]
        }

        TextInput {
            Layout.fillWidth: true
            label: 'Please provide venv path (the "site-packages" directory)'
            placeholder: root.venvPath
        }

        TextInput {
            Layout.fillWidth: true
            visible: _radioGroup.index == 3
            label: 'Compression target path'
        }
    }
}
