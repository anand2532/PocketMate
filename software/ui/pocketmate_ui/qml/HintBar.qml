import QtQuick
import "."
// Zone 424-480: back gesture · volume-key role · Action-key role
Rectangle {
    property string leftText: ""
    property string midText: "Vol ±: move focus · both: open"
    property string rightText: "Action hold: Talk"
    width: 800; height: 56; color: Theme.chrome
    Text { x: 16; anchors.verticalCenter: parent.verticalCenter; text: parent.leftText; color: Theme.text2
           font { family: Theme.font; pixelSize: Theme.caption } }
    Text { anchors.centerIn: parent; text: parent.midText; color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption } }
    Text { anchors { right: parent.right; rightMargin: 16; verticalCenter: parent.verticalCenter }
           text: parent.rightText; color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption } }
}
