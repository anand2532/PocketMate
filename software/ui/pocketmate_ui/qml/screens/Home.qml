import QtQuick
import ".."
// 01 home
Item {
    Text { x: 16; y: 18; text: "Good " + (new Date().getHours() < 12 ? "morning" : new Date().getHours() < 17 ? "afternoon" : "evening")
           color: Theme.text; font { family: Theme.font; pixelSize: Theme.h1 + 2; bold: true } }
    Text { x: 16; y: 58; text: pm.demo ? "Demo data · services not connected" : "Next: " + (pm.tasks.length ? pm.tasks[0].title : "nothing due")
           color: Theme.text2; font { family: Theme.font; pixelSize: Theme.caption + 2 } }
    Grid {
        x: 16; y: 96; columns: 3; spacing: 12
        Tile { label: "Ask"; primary: true; onClicked: pm.go("listening") }
        Tile { label: "Capture"; onClicked: pm.go("listening") }
        Tile { label: "Memory"; focused: true; onClicked: pm.go("memory") }
        Tile { label: "Scan text"; onClicked: pm.go("home") }      // Camera module: TODO
        Tile { label: "Tasks"; onClicked: pm.go("tasks") }
        Tile { label: "Battery"; onClicked: pm.go("battery") }
    }
}
