import QtQuick
import ".."
// 02 PTT listening: green only while the mic rail is really on (pm-power MicRail signal)
Item {
    BackButton { x: 16; y: 16 }
    Rectangle { id: ring; width: 150; height: 150; radius: 75; anchors.horizontalCenter: parent.horizontalCenter; y: 56
                color: "transparent"; border.width: 6; border.color: pm.mic === "rec" ? Theme.listening : Theme.line
        SequentialAnimation on scale { running: pm.mic === "rec"; loops: Animation.Infinite
            NumberAnimation { to: 1.06; duration: 600 } NumberAnimation { to: 1.0; duration: 600 } }
        // mic glyph drawn with rectangles (no emoji font on the device image)
        Rectangle { width: 34; height: 56; radius: 17; anchors.horizontalCenter: parent.horizontalCenter; y: 34; color: Theme.text }
        Rectangle { width: 6; height: 20; anchors.horizontalCenter: parent.horizontalCenter; y: 92; color: Theme.text }
        Rectangle { width: 40; height: 6; radius: 3; anchors.horizontalCenter: parent.horizontalCenter; y: 110; color: Theme.text } }
    Text { anchors.horizontalCenter: parent.horizontalCenter; y: 230
           text: pm.mic === "rec" ? "Listening…" : pm.mic === "muted" ? "Mic is muted" : "Hold Action to talk"
           color: pm.mic === "muted" ? Theme.error : Theme.text; font { family: Theme.font; pixelSize: Theme.display; bold: true } }
    Text { anchors.horizontalCenter: parent.horizontalCenter; y: 280; text: "On-device · nothing leaves PocketMate"
           color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption + 1 } }
}
