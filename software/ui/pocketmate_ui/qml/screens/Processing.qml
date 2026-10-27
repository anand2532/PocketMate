import QtQuick
import ".."
// 03 processing (local model). Cloud variant 03b: TODO with pm-cloud wiring.
Item {
    Rectangle { width: 120; height: 120; radius: 60; anchors.horizontalCenter: parent.horizontalCenter; y: 70
                color: "transparent"; border.width: 6; border.color: Theme.processing
        RotationAnimation on rotation { from: 0; to: 360; duration: 1400; loops: Animation.Infinite }
        Rectangle { width: 18; height: 18; radius: 9; color: Theme.processing; x: 51; y: -6 } }
    Text { anchors.horizontalCenter: parent.horizontalCenter; y: 220; text: "Thinking…"; color: Theme.text
           font { family: Theme.font; pixelSize: Theme.display; bold: true } }
    Text { anchors.horizontalCenter: parent.horizontalCenter; y: 268; text: "local model"; color: Theme.processing
           font { family: Theme.font; pixelSize: Theme.caption + 1; bold: true } }
}
