import QtQuick
import QtQuick.Window
import "."
import "screens"
// 800x480 landscape root (§4). Fixed zones: status 0-40, content 40-424, hint 424-480.
Window {
    id: root
    width: 800; height: 480; visible: true; color: Theme.bg
    title: "PocketMate"
    StatusBar { id: status; y: 0 }
    Item {
        id: content; y: 40; width: 800; height: 384
        Loader {
            anchors.fill: parent
            source: ({ home: "screens/Home.qml", listening: "screens/Listening.qml", processing: "screens/Processing.qml",
                       response: "screens/Response.qml", memory: "screens/Memory.qml", tasks: "screens/Tasks.qml",
                       battery: "screens/Battery.qml" })[pm.screen] || "screens/Home.qml"
        }
    }
    HintBar {
        y: 424
        leftText: pm.screen === "home" ? "" : "‹ Back"
        midText: pm.screen === "listening" ? "Release Action to send" : "Vol ±: move focus · both: open"
        rightText: pm.screen === "listening" ? "" : "Action hold: Talk"
    }
}
