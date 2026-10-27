pragma Singleton
import QtQuick
// Tokens from design/design-system.md (dark default). Light theme: TODO (Settings › Theme).
QtObject {
    readonly property color bg: "#0F1115"
    readonly property color surface: "#1A1D23"
    readonly property color surface2: "#252932"
    readonly property color text: "#E8EAED"
    readonly property color text2: "#A8AEB4"
    readonly property color accent: "#4C8DFF"
    readonly property color accentText: "#FFFFFF"
    readonly property color listening: "#2ECC71"
    readonly property color processing: "#F5A623"
    readonly property color error: "#FF5A5F"
    readonly property color chrome: "#000000"
    readonly property color line: "#3A3F48"
    readonly property int margin: 16
    readonly property int display: 30
    readonly property int h1: 28
    readonly property int h2: 23
    readonly property int body: 19
    readonly property int caption: 16
    readonly property string font: "DejaVu Sans"
}
