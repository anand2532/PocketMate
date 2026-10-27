import QtQuick
import ".."
// 15 battery (thresholds 20/10/3 % are locked UX parameters)
Item {
    BackButton { x: 16; y: 16 }
    Text { x: 88; y: 26; text: "Battery"; color: Theme.text; font { family: Theme.font; pixelSize: Theme.h1; bold: true } }
    Text { x: 88; y: 84; text: pm.battery + "%"; color: pm.battery <= 10 ? Theme.error : pm.battery <= 20 ? Theme.processing : Theme.text
           font { family: Theme.font; pixelSize: 64; bold: true } }
    Text { x: 88; y: 170; text: pm.charging ? "Charging" : "On battery"; color: Theme.text2; font { family: Theme.font; pixelSize: Theme.body } }
    Text { x: 88; y: 210; visible: pm.lte !== "off"
           text: "Mobile data: " + ({ allow: "on", throttle: "reduced (high load)", block: "paused (battery low)",
                                       shutdown: "off (battery critical)" })[pm.lte] || pm.lte
           color: Theme.text2; font { family: Theme.font; pixelSize: Theme.body } }
}
