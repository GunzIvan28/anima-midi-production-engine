import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    width: 1680
    height: 940
    minimumWidth: 1280
    minimumHeight: 760
    visible: true
    title: "ANIMA MIDI PRODUCTION ENGINE"
    color: "#090d0f"

    readonly property color bg: "#090d0f"
    readonly property color panel: "#111719"
    readonly property color raised: "#171d1f"
    readonly property color border: "#303738"
    readonly property color gold: "#d5a64e"
    readonly property color paleGold: "#ead39e"
    readonly property color text: "#e9e3d6"
    readonly property color muted: "#9b9d96"
    readonly property color teal: "#53d0bd"
    readonly property bool compact: width < 1500
    readonly property int railWidth: compact ? 72 : 94
    readonly property int suiteWidth: compact ? 225 : 282
    readonly property int setupWidth: compact ? 350 : 455
    readonly property int trackHeaderWidth: compact ? 128 : 170
    property var catalog: backend.engineCatalog
    property int engineIndex: 0
    property int moodIndex: 0
    property int sectionIndex: 1
    property string selectedKey: "C"
    property string selectedInstrument: "Violin"
    property int selectedBpm: 96
    property int selectedBars: 4
    property int selectedSeed: 813742
    property bool loopOn: true
    property var engine: catalog.length > engineIndex ? catalog[engineIndex] : ({})
    property var moods: engine.moods || []
    property string mood: moods.length > moodIndex ? moods[moodIndex].name : ""
    property var composition: backend.composition
    property var allCompositionTracks: composition.tracks && composition.tracks.length ? composition.tracks : []
    property var displayTracks: allCompositionTracks.length ? allCompositionTracks.slice(0, 8) : [
        {"name":"Guitar Arpeggio","channel":1,"notes":56}, {"name":"Bass","channel":2,"notes":18},
        {"name":"Trumpet","channel":3,"notes":30}, {"name":"Violin","channel":4,"notes":38},
        {"name":"Counter Melody","channel":5,"notes":42}, {"name":"Percussion","channel":10,"notes":48},
        {"name":"Shaker","channel":10,"notes":64}, {"name":"Tambourine","channel":10,"notes":28}
    ]
    property var displayProgression: composition.progression && composition.progression.length ? composition.progression : ["i", "♭VI", "♭III", "♭VII"]

    font.family: "Segoe UI"
    font.pixelSize: 12

    component Frame: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#171d1f" }
            GradientStop { position: 0.12; color: "#111719" }
            GradientStop { position: 1.0; color: "#0d1213" }
        }
        border.color: window.border
        border.width: 1
        radius: 2
    }
    component TinyTitle: Label {
        color: window.paleGold
        font.pixelSize: 10
        font.weight: Font.DemiBold
        font.letterSpacing: 1.4
    }
    component DarkButton: Button {
        id: control
        implicitHeight: 38
        property color accent: window.gold
        contentItem: Text {
            text: control.text
            color: control.enabled ? window.text : "#77776f"
            font.pixelSize: 10
            font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            gradient: Gradient {
                GradientStop { position: 0.0; color: control.down ? "#111516" : control.hovered ? "#303234" : "#24292a" }
                GradientStop { position: 0.48; color: control.down ? "#0b0e0f" : "#181d1e" }
                GradientStop { position: 1.0; color: "#0a0e0f" }
            }
            border.color: control.hovered || control.activeFocus ? control.accent : "#45494a"
            radius: 2
            Rectangle { anchors.fill: parent; anchors.margins: 2; color: "transparent"; border.color: "#161a1b"; radius: 1 }
        }
    }
    component DarkCombo: ComboBox {
        id: combo
        implicitHeight: 34
        contentItem: Text { leftPadding: 10; text: combo.displayText; color: window.text; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
        indicator: Text { x: combo.width - width - 10; y: (combo.height - height) / 2; text: "▾"; color: window.paleGold; font.pixelSize: 12 }
        background: Rectangle {
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#1e2324" }
                GradientStop { position: 0.35; color: "#111617" }
                GradientStop { position: 1.0; color: "#090d0e" }
            }
            border.color: combo.activeFocus ? window.gold : "#484b4b"
            radius: 2
            Rectangle { anchors.fill: parent; anchors.margins: 2; color: "transparent"; border.color: "#101415" }
        }
        popup: Popup {
            y: combo.height + 2
            width: combo.width
            padding: 3
            implicitHeight: Math.min(contentItem.implicitHeight + 6, 300)
            background: Rectangle { color: "#151b1d"; border.color: window.border }
            contentItem: ListView { clip: true; implicitHeight: contentHeight; model: combo.popup.visible ? combo.delegateModel : null; currentIndex: combo.highlightedIndex; ScrollIndicator.vertical: ScrollIndicator { } }
        }
        delegate: ItemDelegate {
            width: combo.width - 6
            contentItem: Text { text: modelData; color: window.text; verticalAlignment: Text.AlignVCenter }
            background: Rectangle { color: highlighted ? "#30291d" : "transparent" }
            highlighted: combo.highlightedIndex === index
        }
    }
    component MixerToggle: Rectangle {
        id: toggle
        property string label: "M"
        property bool checked: false
        implicitWidth: 18
        implicitHeight: 18
        radius: 1
        color: checked ? "#5a431e" : "#121718"
        border.color: checked ? window.gold : window.border
        Text { anchors.centerIn: parent; text: toggle.label; color: checked ? window.paleGold : window.muted; font.pixelSize: 7; font.weight: Font.Bold }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: toggle.checked = !toggle.checked }
        ToolTip.visible: toolMouse.containsMouse
        ToolTip.text: label === "M" ? "Mute — inactive until playback is integrated" : "Solo — inactive until playback is integrated"
        MouseArea { id: toolMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
    }
    component StudioSlider: Slider {
        id: studioSlider
        implicitHeight: orientation === Qt.Horizontal ? 30 : 150
        implicitWidth: orientation === Qt.Horizontal ? 220 : 28
        background: Rectangle {
            x: studioSlider.orientation === Qt.Horizontal ? studioSlider.leftPadding : (studioSlider.width - width) / 2
            y: studioSlider.orientation === Qt.Horizontal ? (studioSlider.height - height) / 2 : studioSlider.topPadding
            width: studioSlider.orientation === Qt.Horizontal ? studioSlider.availableWidth : 7
            height: studioSlider.orientation === Qt.Horizontal ? 7 : studioSlider.availableHeight
            radius: 3
            color: "#070a0b"
            border.color: "#353a3a"
            Rectangle {
                x: 2
                y: studioSlider.orientation === Qt.Horizontal ? 2 : parent.height * (1 - studioSlider.visualPosition)
                width: studioSlider.orientation === Qt.Horizontal ? parent.width * studioSlider.visualPosition - 4 : parent.width - 4
                height: studioSlider.orientation === Qt.Horizontal ? parent.height - 4 : parent.height * studioSlider.visualPosition - 2
                color: studioSlider.orientation === Qt.Horizontal ? "#8e7445" : "#456b50"
                opacity: 0.8
                radius: 2
            }
        }
        handle: Rectangle {
            x: studioSlider.orientation === Qt.Horizontal ? studioSlider.leftPadding + studioSlider.visualPosition * (studioSlider.availableWidth - width) : (studioSlider.width - width) / 2
            y: studioSlider.orientation === Qt.Horizontal ? (studioSlider.height - height) / 2 : studioSlider.topPadding + studioSlider.visualPosition * (studioSlider.availableHeight - height)
            implicitWidth: studioSlider.orientation === Qt.Horizontal ? 20 : 22
            implicitHeight: studioSlider.orientation === Qt.Horizontal ? 20 : 10
            radius: studioSlider.orientation === Qt.Horizontal ? 10 : 2
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#c3aa7a" }
                GradientStop { position: 0.42; color: "#6d6048" }
                GradientStop { position: 0.55; color: "#252728" }
                GradientStop { position: 1.0; color: "#090b0c" }
            }
            border.color: "#a88a55"
        }
    }
    component StudioDial: Dial {
        id: studioDial
        background: Rectangle {
            x: (studioDial.width - width) / 2
            y: (studioDial.height - height) / 2
            width: Math.min(studioDial.width, studioDial.height)
            height: width
            radius: width / 2
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#655b48" }
                GradientStop { position: 0.18; color: "#242728" }
                GradientStop { position: 0.7; color: "#090c0d" }
                GradientStop { position: 1.0; color: "#2b2e2e" }
            }
            border.color: "#8b744b"
            Rectangle {
                width: 2
                height: parent.height * 0.3
                radius: 1
                color: window.paleGold
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 3
                transformOrigin: Item.Bottom
                rotation: studioDial.angle
            }
        }
        handle: Item { }
    }
    component StudioStepper: SpinBox {
        id: stepper
        editable: true
        contentItem: TextInput { text: stepper.textFromValue(stepper.value, stepper.locale); color: window.text; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; selectByMouse: true; readOnly: !stepper.editable; validator: stepper.validator }
        up.indicator: Rectangle { x: stepper.width - width; height: stepper.height; implicitWidth: 38; color: stepper.up.pressed ? "#372b1a" : "#202526"; border.color: window.border; Text { anchors.centerIn: parent; text: "+"; color: window.paleGold; font.pixelSize: 18 } }
        down.indicator: Rectangle { x: 0; height: stepper.height; implicitWidth: 38; color: stepper.down.pressed ? "#372b1a" : "#202526"; border.color: window.border; Text { anchors.centerIn: parent; text: "−"; color: window.paleGold; font.pixelSize: 18 } }
        background: Rectangle { color: "#090d0e"; border.color: "#484b4b"; radius: 2 }
    }

    Rectangle {
        id: titleBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 50
        color: "#0a0e0f"
        border.color: window.border
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            Label { text: "◬"; color: window.gold; font.pixelSize: 27 }
            Label { text: "ANIMA MIDI PRODUCTION ENGINE"; color: window.paleGold; font.family: "Georgia"; font.pixelSize: 19; font.letterSpacing: 1.5 }
            Item { Layout.fillWidth: true }
            Label { text: backend.progressText; color: backend.busy ? window.gold : window.muted; font.pixelSize: 9 }
            Label { text: "—     □     ×"; color: window.paleGold; font.pixelSize: 15 }
        }
    }

    GridLayout {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: titleBar.bottom
        anchors.bottom: parent.bottom
        anchors.margins: 6
        columns: 4
        columnSpacing: 5
        rowSpacing: 5

        Frame {
            Layout.preferredWidth: window.railWidth
            Layout.minimumWidth: window.railWidth
            Layout.maximumWidth: window.railWidth
            Layout.fillHeight: true
            Layout.rowSpan: 2
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 5
                Repeater {
                    model: [{"icon":"⌂","name":"HOME"},{"icon":"✎","name":"COMPOSE"},{"icon":"♫","name":"IMPORT MIDI"},{"icon":"▤","name":"LIBRARY"},{"icon":"⚙","name":"SETTINGS"}]
                    Rectangle {
                        required property var modelData
                        required property int index
                        Layout.fillWidth: true
                        Layout.preferredHeight: window.compact ? 68 : 82
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: window.sectionIndex === index ? "#5a401b" : "#171c1d" }
                            GradientStop { position: 0.35; color: window.sectionIndex === index ? "#302316" : "#111617" }
                            GradientStop { position: 1.0; color: "#090d0e" }
                        }
                        border.color: window.sectionIndex === index ? window.gold : "transparent"
                        radius: 3
                        Column {
                            anchors.centerIn: parent
                            spacing: 6
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.icon; color: window.sectionIndex === index ? window.gold : window.paleGold; font.pixelSize: window.compact ? 22 : 27 }
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: modelData.name; color: window.sectionIndex === index ? window.paleGold : window.muted; font.pixelSize: 8; font.weight: Font.DemiBold }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                window.sectionIndex = index
                                if (index === 2) backend.chooseInputMidi()
                                if (index === 3) backend.openOutputDirectory()
                            }
                        }
                    }
                }
                Item { Layout.fillHeight: true }
                Label { Layout.alignment: Qt.AlignHCenter; text: "◬"; color: window.gold; font.pixelSize: 32 }
            }
        }

        Frame {
            Layout.preferredWidth: window.suiteWidth
            Layout.minimumWidth: window.suiteWidth
            Layout.maximumWidth: window.suiteWidth
            Layout.fillHeight: true
            Layout.rowSpan: 2
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    color: "#151b1d"
                    border.color: window.border
                    Label { anchors.centerIn: parent; text: "ENGINE SUITE"; color: window.paleGold; font.pixelSize: 11; font.letterSpacing: 1.5 }
                }
                ListView {
                    id: engineList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.margins: 8
                    clip: true
                    spacing: 5
                    model: window.catalog
                    ScrollBar.vertical: ScrollBar { }
                    delegate: Item {
                        required property var modelData
                        required property int index
                        width: engineList.width
                        height: 59
                        TinyTitle { anchors.left: parent.left; anchors.top: parent.top; text: modelData.group }
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            height: 39
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: window.engineIndex === index ? "#61431a" : "#282d2e" }
                                GradientStop { position: 0.16; color: window.engineIndex === index ? "#342515" : "#1b2021" }
                                GradientStop { position: 1.0; color: "#0c1011" }
                            }
                            border.color: window.engineIndex === index ? window.gold : window.border
                            radius: 2
                            Rectangle { anchors.fill: parent; anchors.margins: 2; color: "transparent"; border.color: window.engineIndex === index ? "#6f542a" : "#111516"; radius: 1 }
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 10
                                anchors.rightMargin: 8
                                Text { text: index % 3 === 0 ? "☷" : index % 3 === 1 ? "♬" : "◉"; color: modelData.accent; font.pixelSize: 16 }
                                Text { Layout.fillWidth: true; text: modelData.name; color: window.text; font.pixelSize: 10; elide: Text.ElideRight }
                                Text { text: "›"; color: window.paleGold; font.pixelSize: 18 }
                            }
                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    window.engineIndex = index
                                    window.moodIndex = 0
                                    window.selectedBars = modelData.bars[0]
                                    if (modelData.requiresInput) backend.chooseInputMidi()
                                }
                            }
                        }
                    }
                }
            }
        }

        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true
            ColumnLayout {
                anchors.fill: parent
                spacing: 0
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 42
                    color: "#151b1d"
                    border.color: window.border
                    Label { anchors.centerIn: parent; text: "COMPOSITION WORKSPACE"; color: window.paleGold; font.pixelSize: 12; font.letterSpacing: 1.8 }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 76
                    Layout.minimumHeight: 76
                    Layout.maximumHeight: 76
                    spacing: 0
                    Rectangle { Layout.preferredWidth: window.trackHeaderWidth; Layout.minimumWidth: window.trackHeaderWidth; Layout.fillHeight: true; color: "#101617"; border.color: window.border; Label { anchors.centerIn: parent; text: "CHORD LANE"; color: window.paleGold; font.pixelSize: 9; font.letterSpacing: 1.1 } }
                    Repeater {
                        model: 4
                        Rectangle {
                            required property int index
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: index % 2 ? "#101516" : "#121819"
                            border.color: window.border
                            Column {
                                anchors.centerIn: parent
                                spacing: 8
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: "BAR " + (index + 1); color: window.paleGold; font.pixelSize: 8; font.letterSpacing: 1.2 }
                                Text { anchors.horizontalCenter: parent.horizontalCenter; text: window.displayProgression[index % window.displayProgression.length]; color: window.text; font.family: "Georgia"; font.pixelSize: 19 }
                            }
                        }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 360
                    color: "#0c1112"
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 0
                        Repeater {
                            model: window.displayTracks
                            Rectangle {
                                id: lane
                                required property var modelData
                                required property int index
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.preferredHeight: 68
                                Layout.minimumHeight: 48
                                color: index % 2 ? "#101516" : "#0d1314"
                                border.color: "#2a3132"
                                property color laneColor: ["#e4683f", "#d9a640", "#52c1ad", "#9b67c7", "#dc603e", "#5a9acb", "#a36eb8", "#c39742"][index % 8]
                                RowLayout {
                                    anchors.fill: parent
                                    spacing: 0
                                    Rectangle {
                            Layout.preferredWidth: window.trackHeaderWidth
                            Layout.minimumWidth: window.trackHeaderWidth
                                        Layout.fillHeight: true
                                        color: "#141a1b"
                                        border.color: window.border
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 7
                                            anchors.rightMargin: 5
                                            Rectangle { Layout.preferredWidth: 24; Layout.fillHeight: true; color: lane.laneColor; opacity: 0.65; Text { anchors.centerIn: parent; text: lane.index + 1; color: window.text; font.pixelSize: 11 } }
                                            Text { text: lane.index % 3 === 0 ? "♬" : lane.index % 3 === 1 ? "𝄢" : "♩"; color: window.paleGold; font.pixelSize: 18 }
                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 2
                                                Text { Layout.fillWidth: true; text: lane.modelData.name; color: window.text; font.pixelSize: 9; elide: Text.ElideRight }
                                                Text { text: window.engine.name || "ANIMA"; color: window.gold; font.pixelSize: 7 }
                                            }
                                            Column {
                                                spacing: 3
                                                Rectangle { width: 20; height: 17; color: "#1b2122"; border.color: window.border; Text { anchors.centerIn: parent; text: "M"; color: window.text; font.pixelSize: 7 } }
                                                Rectangle { width: 20; height: 17; color: "#1b2122"; border.color: window.border; Text { anchors.centerIn: parent; text: "S"; color: window.text; font.pixelSize: 7 } }
                                            }
                                        }
                                    }
                                    Repeater {
                                        model: 4
                                        Rectangle {
                                            required property int index
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            color: "transparent"
                                            border.color: window.border
                                            Repeater {
                                                model: Math.max(3, Math.min(14, Math.round(lane.modelData.notes / 5)))
                                                Rectangle {
                                                    required property int index
                                                    property real usable: Math.max(30, parent.width - 18)
                                                    x: 6 + ((index * 31 + lane.index * 17) % usable)
                                                    y: 10 + ((index * 13 + lane.index * 11) % Math.max(12, parent.height - 24))
                                                    width: 8 + (index % 4) * 6
                                                    height: 5
                                                    color: lane.laneColor
                                                    opacity: 0.9
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Frame {
            Layout.preferredWidth: window.setupWidth
            Layout.minimumWidth: window.setupWidth
            Layout.maximumWidth: window.setupWidth
            Layout.fillHeight: true
            ColumnLayout {
                anchors.fill: parent
                spacing: 5
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 42; color: "#151b1d"; border.color: window.border; Label { anchors.centerIn: parent; text: "ENGINE SETUP"; color: window.paleGold; font.pixelSize: 12; font.letterSpacing: 1.7 } }
                GridLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 16
                    Layout.rightMargin: 16
                    columns: 2
                    rowSpacing: 9
                    columnSpacing: 10
                    TinyTitle { text: "KEY" }
                    DarkCombo { Layout.fillWidth: true; model: ["C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"]; onActivated: window.selectedKey = currentText }
                    TinyTitle { text: "MOOD" }
                    DarkCombo { Layout.fillWidth: true; model: window.moods.map(function(x) { return x.name }); onActivated: window.moodIndex = currentIndex }
                    TinyTitle { text: "BPM" }
                    StudioStepper { Layout.fillWidth: true; from: 50; to: 190; value: window.selectedBpm; onValueModified: window.selectedBpm = value }
                    TinyTitle { text: "BARS" }
                    DarkCombo { Layout.fillWidth: true; model: window.engine.bars || [4]; onActivated: window.selectedBars = Number(currentText) }
                    TinyTitle { text: "INSTRUMENT"; visible: window.engine.id === "solo_major" || window.engine.id === "solo_minor" }
                    DarkCombo { Layout.fillWidth: true; visible: window.engine.id === "solo_major" || window.engine.id === "solo_minor"; model: ["Violin","Viola","Cello"]; onActivated: window.selectedInstrument = currentText }
                }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: window.border }
                GridLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 16
                    Layout.rightMargin: 16
                    columns: 2
                    TinyTitle { text: "TENSION" }
                    StudioSlider { Layout.fillWidth: true; from: 0; to: 1; value: 0.58; ToolTip.visible: hovered; ToolTip.text: "Visual control — engine mapping will be added later" }
                    TinyTitle { text: "COMPLEXITY" }
                    StudioSlider { Layout.fillWidth: true; from: 0; to: 1; value: 0.52; ToolTip.visible: hovered; ToolTip.text: "Visual control — engine mapping will be added later" }
                    TinyTitle { text: "SEED" }
                    RowLayout {
                        Layout.fillWidth: true
                        TextField {
                            Layout.fillWidth: true
                            text: String(window.selectedSeed)
                            color: window.text
                            validator: IntValidator { bottom: 1; top: 99999999 }
                            onEditingFinished: window.selectedSeed = Number(text)
                            background: Rectangle { color: "#0d1213"; border.color: window.border }
                        }
                        DarkButton { text: "⚄"; Layout.preferredWidth: 40; onClicked: window.selectedSeed = backend.createSeed() }
                    }
                    TinyTitle { text: "OUTPUT" }
                    RowLayout {
                        Layout.fillWidth: true
                        Text { Layout.fillWidth: true; text: backend.outputDirectory; color: window.muted; elide: Text.ElideMiddle; font.pixelSize: 8 }
                        DarkButton { text: "□"; Layout.preferredWidth: 40; onClicked: backend.chooseOutputDirectory() }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: window.border }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 12
                    Layout.rightMargin: 12
                    TinyTitle { text: "PERFORMANCE MIXER" }
                    Item { Layout.fillWidth: true }
                    Text { text: "⌃"; color: window.paleGold }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    spacing: 2
                    Repeater {
                        model: window.displayTracks
                        Rectangle {
                            required property var modelData
                            required property int index
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#101516"
                            border.color: window.border
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 3
                                Text { Layout.fillWidth: true; text: modelData.name.substring(0, window.compact ? 4 : 6).toUpperCase(); color: window.paleGold; horizontalAlignment: Text.AlignHCenter; font.pixelSize: 6; elide: Text.ElideRight }
                                StudioDial { Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: window.compact ? 28 : 34; Layout.preferredHeight: window.compact ? 28 : 34; from: -1; to: 1; value: 0; ToolTip.visible: hovered; ToolTip.text: "Pan — inactive until playback is integrated" }
                                RowLayout {
                                    Layout.alignment: Qt.AlignHCenter
                                    spacing: 1
                                    MixerToggle { label: "M" }
                                    MixerToggle { label: "S" }
                                }
                                StudioSlider { Layout.fillHeight: true; Layout.alignment: Qt.AlignHCenter; orientation: Qt.Vertical; from: 0; to: 127; value: 92 - index * 3; ToolTip.visible: hovered; ToolTip.text: "Volume — inactive until playback is integrated" }
                                Text { Layout.alignment: Qt.AlignHCenter; text: (-2 - index * 0.7).toFixed(1); color: window.text; font.pixelSize: 7 }
                            }
                        }
                    }
                }
            }
        }

        Frame {
            Layout.row: 1
            Layout.column: 2
            Layout.columnSpan: 2
            Layout.fillWidth: true
            Layout.preferredHeight: 112
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10
                RowLayout {
                    spacing: 2
                    DarkButton { text: "|◀"; Layout.preferredWidth: window.compact ? 43 : 68; Layout.fillHeight: true; ToolTip.visible: hovered; ToolTip.text: "Inactive transport control" }
                    DarkButton { text: "▶"; Layout.preferredWidth: window.compact ? 43 : 68; Layout.fillHeight: true; ToolTip.visible: hovered; ToolTip.text: "Playback will be incorporated later" }
                    DarkButton { text: "■"; Layout.preferredWidth: window.compact ? 43 : 68; Layout.fillHeight: true; ToolTip.visible: hovered; ToolTip.text: "Playback will be incorporated later" }
                    DarkButton { text: "↻"; Layout.preferredWidth: window.compact ? 43 : 68; Layout.fillHeight: true; onClicked: window.loopOn = !window.loopOn }
                }
                Rectangle {
                    Layout.preferredWidth: window.compact ? 116 : 190
                    Layout.fillHeight: true
                    color: "#101516"
                    border.color: window.border
                    Column {
                        anchors.centerIn: parent
                        spacing: 5
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "00:00:00:00"; color: window.text; font.family: "Consolas"; font.pixelSize: 18 }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: "BAR 1   BEAT 1"; color: window.muted; font.pixelSize: 8 }
                    }
                }
                ColumnLayout {
                    Layout.preferredWidth: window.compact ? 82 : 135
                    TinyTitle { text: "LOOP" }
                    RowLayout {
                        DarkButton { text: "OFF"; accent: !window.loopOn ? window.gold : window.border; onClicked: window.loopOn = false }
                        DarkButton { text: "ON"; accent: window.loopOn ? window.gold : window.border; onClicked: window.loopOn = true }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: window.compact ? 90 : 140
                    TinyTitle { text: "STATUS" }
                    Label { text: "OFFLINE  •  READY"; color: window.teal; font.pixelSize: 16; font.letterSpacing: 1.2 }
                }
                ColumnLayout {
                    Layout.preferredWidth: window.compact ? 105 : 155
                    TinyTitle { text: "SEED" }
                    RowLayout {
                        TextField { Layout.fillWidth: true; text: String(window.selectedSeed); color: window.text; background: Rectangle { color: "#0d1213"; border.color: window.border } }
                        DarkButton { text: "⚄"; onClicked: window.selectedSeed = backend.createSeed() }
                    }
                }
                Button {
                    id: generateButton
                    Layout.preferredWidth: window.compact ? 245 : 430
                    Layout.fillHeight: true
                    enabled: !backend.busy && window.mood.length > 0 && (!window.engine.requiresInput || backend.inputFile.length > 0)
                    contentItem: Text { text: backend.busy ? "COMPOSING…" : "GENERATE COMPOSITION"; color: generateButton.enabled ? "#ffe6aa" : "#786b50"; font.family: "Georgia"; font.pixelSize: 20; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    background: Rectangle {
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: generateButton.down ? "#4a351b" : "#745322" }
                            GradientStop { position: 0.18; color: "#3e2d1a" }
                            GradientStop { position: 0.7; color: "#251b12" }
                            GradientStop { position: 1.0; color: "#120e0b" }
                        }
                        border.color: window.gold
                        border.width: 2
                        radius: 3
                        Rectangle { anchors.fill: parent; anchors.margins: 5; color: "transparent"; border.color: "#8c6a34"; opacity: 0.55 }
                        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 3; height: 1; color: "#f0cc79"; opacity: 0.45 }
                    }
                    onClicked: backend.generate({"engine": window.engine.id,"mood":window.mood,"key":window.selectedKey,"bpm":window.selectedBpm,"instrument":window.selectedInstrument,"seed":window.selectedSeed,"bars":window.selectedBars,"inputFile":backend.inputFile})
                }
            }
        }
    }

    Canvas {
        id: surfaceTexture
        anchors.fill: parent
        z: 50
        enabled: false
        opacity: 0.13
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.strokeStyle = "#ffffff"
            ctx.lineWidth = 0.35
            for (var y = 2; y < height; y += 4) {
                ctx.globalAlpha = (y % 12 === 0) ? 0.09 : 0.035
                ctx.beginPath()
                ctx.moveTo(0, y + 0.5)
                ctx.lineTo(width, y + 0.5)
                ctx.stroke()
            }
            ctx.globalAlpha = 0.08
            ctx.fillStyle = "#d8b46d"
            for (var x = 17; x < width; x += 53) {
                for (var py = 19 + (x % 31); py < height; py += 79)
                    ctx.fillRect(x, py, 0.7, 0.7)
            }
        }
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
    }

    Dialog {
        id: errorDialog
        modal: true
        anchors.centerIn: Overlay.overlay
        width: 500
        title: "ANIMA could not complete the request"
        standardButtons: Dialog.Ok
        property string details: ""
        contentItem: Text { text: errorDialog.details; color: window.text; wrapMode: Text.Wrap; width: 450 }
        background: Rectangle { color: window.raised; border.color: "#c96a67" }
    }
    Connections {
        target: backend
        function onCatalogChanged() { window.catalog = backend.engineCatalog; window.engineIndex = 0; window.moodIndex = 0 }
        function onGenerationFailed(message) { errorDialog.details = message; errorDialog.open() }
        function onGenerationCompleted(result) { window.composition = result; window.selectedSeed = backend.createSeed() }
    }
}
