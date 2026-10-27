import QtQuick
import "."
// 248x124 tile (design-system.md "Touch targets"); primary = accent fill; focus = 2 px ring
Rectangle {
    id: tile
    property string label
    property bool primary: false
    property bool focused: false
    signal clicked()
    width: 248; height: 124; radius: 10
    color: primary ? Theme.accent : Theme.surface2
    border.width: focused ? 2 : 0; border.color: Theme.text
    Text { anchors.centerIn: parent; text: tile.label; color: tile.primary ? Theme.accentText : Theme.text
           font { family: Theme.font; pixelSize: Theme.h2; bold: true } }
    MouseArea { anchors.fill: parent; onClicked: tile.clicked() }
}
