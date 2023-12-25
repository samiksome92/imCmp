import QtQuick

Window {
    visible: true
    visibility: "Maximized"
    title: "imCmp"
    color: "black"

    Image {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: path1.top

        focus: true
        source: backEnd.image
        fillMode: Image.PreserveAspectFit

        Keys.onPressed: event => {
            switch (event.key) {
            case Qt.Key_Left:
                backEnd.load_left_image();
                break;
            case Qt.Key_Right:
                backEnd.load_right_image();
                break;
            case Qt.Key_Space:
                backEnd.toggle_image();
                break;
            case Qt.Key_Enter:
            case Qt.Key_Return:
                backEnd.select();
                break;
            case Qt.Key_N:
                backEnd.next();
                break;
            }
        }
    }

    Text {
        id: path1

        anchors.left: parent.left
        anchors.bottom: progressBar.top
        width: 0.4 * parent.width

        text: backEnd.path1
        font.pointSize: 12
        font.family: "Consolas"
        color: backEnd.left ? "black" : "gainsboro"
    }

    Text {
        id: stats1

        anchors.left: path1.right
        anchors.bottom: progressBar.top
        width: 0.08 * parent.width

        text: backEnd.stats1
        textFormat: Text.StyledText
        font.pointSize: 12
        font.family: "Consolas"
        horizontalAlignment: Text.AlignRight
        color: backEnd.left ? "black" : "gainsboro"
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: stats1.right
        anchors.top: path1.top
        anchors.bottom: parent.bottom
        z: -1

        color: backEnd.left ? "gainsboro" : "#00000000"
    }

    Text {
        anchors.left: stats1.right
        anchors.right: stats2.left
        anchors.bottom: progressBar.top

        text: backEnd.score
        font.pointSize: 12
        font.family: "Consolas"
        horizontalAlignment: Text.AlignHCenter
        color: "gainsboro"
    }

    Text {
        id: stats2

        anchors.right: path2.left
        anchors.bottom: progressBar.top
        width: 0.08 * parent.width

        text: backEnd.stats2
        textFormat: Text.StyledText
        font.pointSize: 12
        font.family: "Consolas"
        color: backEnd.left ? "gainsboro" : "black"
    }

    Text {
        id: path2

        anchors.right: parent.right
        anchors.bottom: progressBar.top
        width: 0.4 * parent.width

        text: backEnd.path2
        font.pointSize: 12
        font.family: "Consolas"
        horizontalAlignment: Text.AlignRight
        color: backEnd.left ? "gainsboro" : "black"
    }

    Rectangle {
        anchors.left: stats2.left
        anchors.right: parent.right
        anchors.top: path2.top
        anchors.bottom: parent.bottom
        z: -1

        color: backEnd.left ? "#00000000" : "gainsboro"
    }

    Rectangle {
        id: progressBar

        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: backEnd.progress * parent.width
        height: 2

        color: "limeGreen"
    }

    onClosing: backEnd.show_discarded()
}
