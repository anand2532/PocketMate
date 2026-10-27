import QtQuick
import ".."
// 10 tasks list
Item {
    BackButton { x: 16; y: 16 }
    Text { x: 88; y: 26; text: "Tasks"; color: Theme.text; font { family: Theme.font; pixelSize: Theme.h1; bold: true } }
    Column { x: 88; y: 80; spacing: 8
        Repeater { model: pm.tasks
            Rectangle { width: 696; height: 60; radius: 8; color: Theme.surface
                Rectangle { x: 16; y: 18; width: 24; height: 24; radius: 4; color: modelData.done ? Theme.listening : "transparent"
                            border.color: Theme.text2; border.width: 2
                    Text { anchors.centerIn: parent; text: modelData.done ? "✓" : ""; color: Theme.accentText; font.pixelSize: 16 } }
                Text { x: 56; anchors.verticalCenter: parent.verticalCenter; text: modelData.title; font.strikeout: modelData.done
                       color: modelData.done ? Theme.text2 : Theme.text; font { family: Theme.font; pixelSize: Theme.body } }
                Text { anchors { right: parent.right; rightMargin: 16; verticalCenter: parent.verticalCenter } text: modelData.due
                       color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption } } } } }
    Text { visible: pm.tasks.length === 0; x: 88; y: 90; text: "No tasks"; color: Theme.text2; font { family: Theme.font; pixelSize: Theme.body } }
}
