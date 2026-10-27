import QtQuick
import ".."
// 06 memory search
Item {
    BackButton { x: 16; y: 16 }
    Rectangle { x: 88; y: 16; width: 696; height: 56; radius: 8; color: Theme.surface2; border.color: Theme.accent; border.width: 2
        TextInput { id: q; anchors { fill: parent; margins: 14 } color: Theme.text; text: "parking"
                    font { family: Theme.font; pixelSize: Theme.body + 1 } onAccepted: pm.search(text) } }
    Column { x: 88; y: 88; spacing: 8
        Repeater { model: pm.results
            Rectangle { width: 696; height: 64; radius: 8; color: Theme.surface
                Text { x: 16; y: 9; text: modelData.text; color: Theme.text; width: 664; elide: Text.ElideRight
                       font { family: Theme.font; pixelSize: Theme.body } }
                Text { x: 16; y: 38; text: modelData.source; color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption - 1 } } } } }
}
