import QtQuick
import "."
// Zone 0-40: time · mic pill (centred) · LOCAL/CLOUD · battery (design-system.md "Grid & layout")
Rectangle {
    width: 800; height: 40; color: Theme.chrome
    Text { x: 16; anchors.verticalCenter: parent.verticalCenter; text: pm.clock; color: Theme.text
           font { family: Theme.font; pixelSize: 18; bold: true } }
    Rectangle {
        id: pill; width: 200; height: 24; radius: 12; anchors.centerIn: parent
        color: pm.mic === "rec" ? Theme.listening : pm.mic === "muted" ? Theme.error : Theme.surface2
        Text { anchors.centerIn: parent; color: pm.mic === "ready" ? Theme.text2 : Theme.accentText
               text: pm.mic === "rec" ? "● REC" : pm.mic === "muted" ? "MIC MUTED" : "MIC READY"
               font { family: Theme.font; pixelSize: 15; bold: true } }
    }
    Row {
        anchors { right: parent.right; rightMargin: 10; verticalCenter: parent.verticalCenter }
        spacing: 14
        Text { visible: pm.lte !== "off"; anchors.verticalCenter: parent.verticalCenter
               text: pm.lte === "allow" ? "4G" : pm.lte === "throttle" ? "4G·LOW" : "4G ✈"
               color: pm.lte === "allow" ? Theme.text2 : Theme.processing
               font { family: Theme.font; pixelSize: 15; bold: true } }
        Text { anchors.verticalCenter: parent.verticalCenter; text: pm.cloud ? "CLOUD" : "LOCAL"
               color: pm.cloud ? Theme.processing : Theme.text2; font { family: Theme.font; pixelSize: 15; bold: true } }
        Rectangle {
            width: 60; height: 18; radius: 3; color: "transparent"; border.color: Theme.text; border.width: 1.5
            anchors.verticalCenter: parent.verticalCenter
            Rectangle { x: 3; y: 3; height: parent.height - 6; radius: 2
                        width: (parent.width - 6) * Math.max(0, Math.min(100, pm.battery)) / 100
                        color: pm.battery <= 10 ? Theme.error : pm.battery <= 20 ? Theme.processing : Theme.listening }
        }
        Text { anchors.verticalCenter: parent.verticalCenter; text: (pm.charging ? "⚡" : "") + pm.battery + "%"
               color: Theme.text; font { family: Theme.font; pixelSize: 15; bold: true } }
    }
}
