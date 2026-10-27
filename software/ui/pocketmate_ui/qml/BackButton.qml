import QtQuick
import "."
Rectangle {
    width: 56; height: 56; radius: 8; color: Theme.surface2
    Text { anchors.centerIn: parent; text: "‹"; color: Theme.text; font { family: Theme.font; pixelSize: 34; bold: true } }
    MouseArea { anchors.fill: parent; onClicked: pm.go("home") }
}
