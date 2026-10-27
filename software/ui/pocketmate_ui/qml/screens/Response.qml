import QtQuick
import ".."
// 04 response with source chips (every answer cites its memory source, §8)
Item {
    BackButton { x: 16; y: 16 }
    Rectangle { x: 88; y: 16; width: 696; height: 250; radius: 10; color: Theme.surface
        Text { anchors { fill: parent; margins: 18 } text: pm.answer; wrapMode: Text.WordWrap; color: Theme.text
               font { family: Theme.font; pixelSize: Theme.body + 3 } elide: Text.ElideRight } }
    Row { x: 88; y: 282; spacing: 10
        Repeater { model: pm.sources
            Rectangle { height: 40; width: chip.implicitWidth + 28; radius: 20; color: Theme.surface2; border.color: Theme.line
                Text { id: chip; anchors.centerIn: parent; text: "↗ " + modelData; color: Theme.accent
                       font { family: Theme.font; pixelSize: Theme.caption } } } } }
    Text { visible: pm.sources.length === 0; x: 88; y: 290; text: "No saved source for this answer"; color: Theme.text2
           font { family: Theme.font; pixelSize: Theme.caption } }
}
