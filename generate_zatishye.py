# -*- coding: utf-8 -*-
import json
import pathlib
import wave
import struct
import math
import random

ROOT = pathlib.Path("Zatishye")
SR = 22050

def w(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("  +", path)

def dlg(path, lines):
    w(path, json.dumps({"lines": lines}, ensure_ascii=False, indent=2))

def save_wav(path, samples):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32000)) for s in samples
        ))
    print("  \u266a", path)

# ============================================================
# project.godot
# ============================================================
w("project.godot", """; Engine configuration file.
config_version=5

[application]
config/name="Zatishye"
run/main_scene="res://scenes/MainMenu.tscn"
config/features=PackedStringArray("4.3", "Forward Plus")
config/icon="res://icon.svg"

[autoload]
GameManager="*res://scripts/GameManager.gd"
AudioManager="*res://scripts/AudioManager.gd"
SaveSystem="*res://scripts/SaveSystem.gd"
SanitySystem="*res://scenes/SanitySystem.tscn"
DialogueManager="*res://scenes/DialogueUI.tscn"
AnagramPuzzle="*res://scenes/AnagramPuzzle.tscn"
ClueInventory="*res://scenes/ClueInventory.tscn"

[display]
window/size/viewport_width=1280
window/size/viewport_height=720

[input]
toggle_inventory={
"deadzone": 0.5,
"events": [Object(InputEventKey,"physical_keycode":4194308)]
}

[physics]
common/physics_ticks_per_second=60

[rendering]
renderer/rendering_method="forward_plus"
""")

w("README.md", "# Zatishye\n\nGodot 4.3+. Откройте папку в Godot, нажмите F5.\n\nУправление: WASD — движение, мышь — обзор, E — взаимодействие, TAB — улики, Esc — курсор.\n")
w("icon.svg", '<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg"><rect width="128" height="128" fill="#14141c"/><text x="64" y="82" text-anchor="middle" fill="#a02020" font-size="64" font-family="serif">Z</text></svg>\n')
w(".gitignore", ".godot/\n*.import\nexport/\n")

# ============================================================
# GameManager.gd
# ============================================================
w("scripts/GameManager.gd", """extends Node

const ACTS = [
\t"res://scenes/Act1_Ferry.tscn",
\t"res://scenes/Act2_Asylum.tscn",
\t"res://scenes/Act3_Cell.tscn",
\t"res://scenes/Act4_Lighthouse.tscn",
\t"res://scenes/Act5_Finale.tscn",
]

var current_act: int = -1
var flags: Dictionary = {}
var clues: Array = []

func _ready() -> void:
\tvar actions = {
\t\t"move_forward": KEY_W,
\t\t"move_back": KEY_S,
\t\t"move_left": KEY_A,
\t\t"move_right": KEY_D,
\t\t"interact": KEY_E,
\t\t"sprint": KEY_SHIFT,
\t}
\tfor action in actions:
\t\tif not InputMap.has_action(action):
\t\t\tInputMap.add_action(action)
\t\tvar ev := InputEventKey.new()
\t\tev.physical_keycode = actions[action]
\t\tInputMap.action_add_event(action, ev)

func load_act(index: int) -> void:
\tif has_node("/root/SaveSystem") and index > 0:
\t\tSaveSystem.save_game()
\tcurrent_act = index
\tif index < 0 or index >= ACTS.size():
\t\tget_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
\t\treturn
\tget_tree().paused = false
\tget_tree().change_scene_to_file(ACTS[index])

func next_act() -> void:
\tload_act(current_act + 1)

func set_flag(key: String, value = true) -> void:
\tflags[key] = value

func get_flag(key: String, default = false):
\treturn flags.get(key, default)

func add_clue(clue: String) -> void:
\tif not clues.has(clue):
\t\tclues.append(clue)
\t\tprint("[Clue] + ", clue)
\t\tif has_node("/root/ClueInventory"):
\t\t\tClueInventory.refresh()
""")

# ============================================================
# AudioManager.gd
# ============================================================
w("scripts/AudioManager.gd", """extends Node

var _drone: AudioStreamPlayer
var _sea: AudioStreamPlayer
var _whisper: AudioStreamPlayer

func _ready() -> void:
\t_drone = _mk("res://audio/drone.wav", -18.0, true)
\t_sea = _mk("res://audio/sea.wav", -14.0, true)
\t_whisper = _mk("res://audio/whisper.wav", -20.0, true)

func _mk(path: String, vol: float, loop: bool) -> AudioStreamPlayer:
\tvar p := AudioStreamPlayer.new()
\tp.stream = load(path)
\tif p.stream is AudioStreamWAV:
\t\t(p.stream as AudioStreamWAV).loop_mode = AudioStreamWAV.LOOP_FORWARD if loop else AudioStreamWAV.LOOP_DISABLED
\tp.volume_db = vol
\tadd_child(p)
\treturn p

func play_ambient(kind: String) -> void:
\tstop_all()
\tmatch kind:
\t\t"sea": _sea.play()
\t\t"drone": _drone.play()
\t\t"whisper": _whisper.play()

func play_sfx(path: String, vol: float = 0.0) -> void:
\tvar p := AudioStreamPlayer.new()
\tp.stream = load(path)
\tp.volume_db = vol
\tadd_child(p)
\tp.finished.connect(p.queue_free)
\tp.play()

func play_step() -> void:
\tplay_sfx("res://audio/step.wav", -10.0)

func stop_all() -> void:
\t_drone.stop()
\t_sea.stop()
\t_whisper.stop()
""")

# ============================================================
# SaveSystem.gd
# ============================================================
w("scripts/SaveSystem.gd", """extends Node

const SAVE_PATH := "user://save.json"

func save_game() -> void:
\tvar data := {
\t\t"act": GameManager.current_act,
\t\t"flags": GameManager.flags,
\t\t"clues": GameManager.clues,
\t}
\tvar f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
\tif f == null: return
\tf.store_string(JSON.stringify(data, "\\t"))
\tf.close()

func load_game() -> bool:
\tif not FileAccess.file_exists(SAVE_PATH): return false
\tvar f := FileAccess.open(SAVE_PATH, FileAccess.READ)
\tif f == null: return false
\tvar data = JSON.parse_string(f.get_as_text())
\tf.close()
\tif not (data is Dictionary): return false
\tGameManager.flags = data.get("flags", {})
\tGameManager.clues = data.get("clues", [])
\tGameManager.load_act(int(data.get("act", 0)))
\treturn true

func has_save() -> bool:
\treturn FileAccess.file_exists(SAVE_PATH)

func delete_save() -> void:
\tif has_save():
\t\tDirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
""")

# ============================================================
# PlayerController.gd
# ============================================================
w("scripts/PlayerController.gd", """extends CharacterBody3D

@export var walk_speed: float = 3.0
@export var sprint_speed: float = 5.0
@export var mouse_sensitivity: float = 0.0022
@export var gravity: float = 20.0

@onready var camera: Camera3D = $Camera3D
@onready var ray: RayCast3D = $Camera3D/RayCast3D

var _step_cd: float = 0.0

func _ready() -> void:
\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
\tray.target_position = Vector3(0, 0, -3.5)

func _unhandled_input(event: InputEvent) -> void:
\tif event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
\t\trotate_y(-event.relative.x * mouse_sensitivity)
\t\tcamera.rotate_x(-event.relative.y * mouse_sensitivity)
\t\tcamera.rotation.x = clampf(camera.rotation.x, -1.4, 1.4)
\telif event.is_action_pressed("interact"):
\t\tif ray.is_colliding():
\t\t\tvar t = ray.get_collider()
\t\t\tif t and t.has_method("interact"):
\t\t\t\tt.interact()
\telif event.is_action_pressed("toggle_inventory"):
\t\tClueInventory.toggle()
\telif event.is_action_pressed("ui_cancel"):
\t\tif Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
\t\t\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\t\telse:
\t\t\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _physics_process(delta: float) -> void:
\tif not is_on_floor():
\t\tvelocity.y -= gravity * delta
\telse:
\t\tvelocity.y = 0.0
\tvar d := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
\tvar dir := (transform.basis * Vector3(d.x, 0, d.y)).normalized()
\tvar sp := sprint_speed if Input.is_action_pressed("sprint") else walk_speed
\tvelocity.x = dir.x * sp
\tvelocity.z = dir.z * sp
\tmove_and_slide()
\t_step_cd -= delta
\tif is_on_floor() and Vector2(velocity.x, velocity.z).length() > 0.5 and _step_cd <= 0.0:
\t\t_step_cd = 0.45
\t\tAudioManager.play_step()
""")

# ============================================================
# Interactable.gd
# ============================================================
w("scripts/Interactable.gd", """extends StaticBody3D

@export var dialogue_path: String = ""
@export var one_time: bool = true
@export var requires_flag: String = ""
@export var sets_flag: String = ""
@export var ending: String = ""
@export var clue: String = ""

var used: bool = false

func interact() -> void:
\tif one_time and used: return
\tif requires_flag != "" and not GameManager.get_flag(requires_flag): return
\tused = true
\tif sets_flag != "": GameManager.set_flag(sets_flag, true)
\tif clue != "": GameManager.add_clue(clue)
\tif dialogue_path != "":
\t\tvar lines = DialogueManager.load_dialogue(dialogue_path)
\t\tif lines.size() > 0:
\t\t\tDialogueManager.start_dialogue(lines, ending)
""")

# ============================================================
# AnagramTrigger.gd
# ============================================================
w("scripts/AnagramTrigger.gd", """extends StaticBody3D

@export var target_word: String = "ИВАН КОСТРИН"
@export var hint_text: String = "Переставьте буквы: В И К Т О Р С А Н И Н"

func interact() -> void:
\tif GameManager.get_flag("puzzle_solved"): return
\tAnagramPuzzle.solved.connect(_on_solved, CONNECT_ONE_SHOT)
\tAnagramPuzzle.open(target_word, hint_text)

func _on_solved() -> void:
\tGameManager.set_flag("puzzle_solved", true)
\tGameManager.add_clue("Анаграмма разгадана: ИВАН КОСТРИН")
""")

# ============================================================
# ExitTrigger.gd
# ============================================================
w("scripts/ExitTrigger.gd", """extends Area3D

@export var target_act: int = -1
@export var requires_flag: String = ""

func _ready() -> void:
\tbody_entered.connect(_on_body)

func _on_body(b: Node3D) -> void:
\tif b.name != "Player": return
\tif requires_flag != "" and not GameManager.get_flag(requires_flag): return
\tif target_act >= 0: GameManager.load_act(target_act)
\telse: GameManager.next_act()
""")

# ============================================================
# ActController.gd
# ============================================================
w("scripts/ActController.gd", """extends Node3D

@export var intro_dialogue: String = ""
@export var ambient: String = "drone"

func _ready() -> void:
\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
\tif ambient != "": AudioManager.play_ambient(ambient)
\tif intro_dialogue != "":
\t\tvar key := "seen_" + intro_dialogue
\t\tif not GameManager.get_flag(key):
\t\t\tGameManager.set_flag(key, true)
\t\t\tawait get_tree().process_frame
\t\t\tvar lines = DialogueManager.load_dialogue(intro_dialogue)
\t\t\tif lines.size() > 0:
\t\t\t\tDialogueManager.start_dialogue(lines)
""")

# ============================================================
# MainMenu.gd
# ============================================================
w("scripts/MainMenu.gd", """extends Control

@onready var cont: Button = $VBox/ContinueBtn
@onready var dele: Button = $VBox/DeleteBtn

func _ready() -> void:
\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\tAudioManager.play_ambient("sea")
\tcont.disabled = not SaveSystem.has_save()
\tdele.disabled = not SaveSystem.has_save()

func _on_start_pressed() -> void:
\tGameManager.flags.clear()
\tGameManager.clues.clear()
\tget_tree().change_scene_to_file("res://scenes/Cutscene_Intro.tscn")

func _on_continue_pressed() -> void:
\tSaveSystem.load_game()

func _on_delete_pressed() -> void:
\tSaveSystem.delete_save()
\tcont.disabled = true
\tdele.disabled = true

func _on_quit_pressed() -> void:
\tget_tree().quit()
""")

# ============================================================
# DialogueUI.gd
# ============================================================
w("scripts/DialogueUI.gd", """extends CanvasLayer

signal dialogue_finished

@onready var panel: PanelContainer = $Panel
@onready var speaker_label: Label = $Panel/VBox/Speaker
@onready var text_label: Label = $Panel/VBox/Text
@onready var hint: Label = $Panel/VBox/Hint

var _lines: Array = []
var _i: int = 0
var _active: bool = false
var _ending: String = ""

func _ready() -> void:
\tpanel.hide()
\tprocess_mode = Node.PROCESS_MODE_ALWAYS

func load_dialogue(path: String) -> Array:
\tif not FileAccess.file_exists(path): return []
\tvar f := FileAccess.open(path, FileAccess.READ)
\tif f == null: return []
\tvar data = JSON.parse_string(f.get_as_text())
\tif data is Dictionary and data.has("lines"): return data["lines"]
\treturn []

func start_dialogue(lines: Array, ending: String = "") -> void:
\tif _active or lines.is_empty():
\t\tdialogue_finished.emit()
\t\treturn
\t_lines = lines
\t_i = 0
\t_active = true
\t_ending = ending
\tpanel.show()
\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\tget_tree().paused = true
\t_show()

func _show() -> void:
\tif _i >= _lines.size():
\t\t_end()
\t\treturn
\tvar ln: Dictionary = _lines[_i]
\tspeaker_label.text = String(ln.get("speaker", ""))
\ttext_label.text = String(ln.get("text", ""))
\thint.text = "[E] завершить" if _i == _lines.size() - 1 else "[E] далее"

func _unhandled_input(e: InputEvent) -> void:
\tif not _active: return
\tif e.is_action_pressed("interact"):
\t\tget_viewport().set_input_as_handled()
\t\t_i += 1
\t\t_show()

func _end() -> void:
\t_active = false
\tpanel.hide()
\tget_tree().paused = false
\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
\tvar m := _ending
\t_ending = ""
\tdialogue_finished.emit()
\tif m == "monster" or m == "human":
\t\tawait get_tree().create_timer(0.3).timeout
\t\t_show_ending(m)

func _show_ending(which: String) -> void:
\tpanel.show()
\tif which == "monster":
\t\tspeaker_label.text = "— КОНЕЦ: МОНСТР —"
\t\ttext_label.text = "Бред вернулся. Пациента увели на лоботомию."
\telse:
\t\tspeaker_label.text = "— КОНЕЦ: ЧЕЛОВЕК —"
\t\ttext_label.text = "Он выбрал забыть — и уйти с достоинством."
\thint.text = ""
\tawait get_tree().create_timer(5.0).timeout
\tget_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
""")

# ============================================================
# SanitySystem.gd
# ============================================================
w("scripts/SanitySystem.gd", """extends CanvasLayer

var sanity: float = 100.0
@onready var overlay: ColorRect = $Overlay

func drain(n: float) -> void:
\tsanity = clampf(sanity - n, 0.0, 100.0)
\t_update()

func _update() -> void:
\tvar t := (100.0 - sanity) / 100.0
\toverlay.color = Color(0.4, 0.02, 0.02, t * 0.55)
""")

# ============================================================
# AnagramPuzzle.gd
# ============================================================
w("scripts/AnagramPuzzle.gd", """extends Control

signal solved

@onready var inp: LineEdit = $VBox/Input
@onready var hint: Label = $VBox/Hint
@onready var sub: Button = $VBox/Buttons/Submit
@onready var clo: Button = $VBox/Buttons/Close

var _t: String = ""

func _ready() -> void:
\thide()
\tprocess_mode = Node.PROCESS_MODE_ALWAYS
\tsub.pressed.connect(_submit)
\tclo.pressed.connect(_close)
\tinp.text_submitted.connect(func(_s): _submit())

func open(target: String, hint_text: String) -> void:
\t_t = target.to_upper().replace(" ", "")
\thint.text = hint_text
\tinp.text = ""
\tshow()
\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\tget_tree().paused = true
\tinp.grab_focus()

func _submit() -> void:
\tvar g := inp.text.to_upper().replace(" ", "")
\tif g == _t:
\t\thint.text = "ВЕРНО."
\t\tawait get_tree().create_timer(1.0).timeout
\t\tsolved.emit()
\t\t_close()
\telse:
\t\thint.text = "Не складывается. Попробуйте ещё."
\t\tSanitySystem.drain(5.0)

func _close() -> void:
\thide()
\tget_tree().paused = false
\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
""")

# ============================================================
# ClueInventory.gd
# ============================================================
w("scripts/ClueInventory.gd", """extends CanvasLayer

@onready var panel: PanelContainer = $Panel
@onready var list: VBoxContainer = $Panel/Margin/VBox/Scroll/List
@onready var title: Label = $Panel/Margin/VBox/Title
var _open: bool = false

func _ready() -> void:
\tpanel.hide()
\tprocess_mode = Node.PROCESS_MODE_ALWAYS

func toggle() -> void:
\tif _open: _close() else: open()

func open() -> void:
\trefresh()
\tpanel.show()
\t_open = true
\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\tget_tree().paused = true

func _close() -> void:
\tpanel.hide()
\t_open = false
\tget_tree().paused = false
\tInput.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func refresh() -> void:
\tif not is_inside_tree(): return
\tfor c in list.get_children(): c.queue_free()
\ttitle.text = "УЛИКИ (%d)" % GameManager.clues.size()
\tif GameManager.clues.is_empty():
\t\tvar l := Label.new(); l.text = "Пока ничего."; list.add_child(l); return
\tfor c in GameManager.clues:
\t\tvar l := Label.new()
\t\tl.text = "• " + str(c)
\t\tl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
\t\tlist.add_child(l)
""")

# ============================================================
# Cutscene.gd
# ============================================================
w("scripts/Cutscene.gd", """extends Node3D

@export var frames: Array[String] = []
@export var durations: Array[float] = []
@export var ambient: String = "sea"
@export var next_scene: String = ""

@onready var label: Label = $UI/Center/Text
@onready var hint: Label = $UI/Bottom/Subtitle

var _i: int = 0
var _skip: bool = false

func _ready() -> void:
\tInput.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
\tif ambient != "": AudioManager.play_ambient(ambient)
\t_advance()

func _advance() -> void:
\tif _skip or _i >= frames.size():
\t\t_finish()
\t\treturn
\tlabel.text = frames[_i]
\tvar dur: float = durations[_i] if _i < durations.size() else 3.0
\tawait get_tree().create_timer(dur).timeout
\t_i += 1
\t_advance()

func _unhandled_input(e: InputEvent) -> void:
\tif e is InputEventKey and e.pressed and e.physical_keycode == KEY_SPACE:
\t\t_skip = true
\telif e is InputEventMouseButton and e.pressed:
\t\t_skip = true

func _finish() -> void:
\tAudioManager.stop_all()
\tif next_scene != "":
\t\tget_tree().change_scene_to_file(next_scene)
\telse:
\t\tGameManager.load_act(0)
""")

# ============================================================
# TSCN — MainMenu
# ============================================================
w("scenes/MainMenu.tscn", """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/MainMenu.gd" id="1"]

[node name="MainMenu" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1")

[node name="BG" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0.04, 0.04, 0.06, 1)

[node name="Title" type="Label" parent="."]
layout_mode = 1
anchors_preset = 10
anchor_right = 1.0
offset_top = 100.0
offset_bottom = 200.0
theme_override_colors/font_color = Color(0.7, 0.1, 0.1, 1)
theme_override_font_sizes/font_size = 72
text = "ЗАТИШЬЕ"
horizontal_alignment = 1

[node name="VBox" type="VBoxContainer" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -150.0
offset_top = 20.0
offset_right = 150.0
offset_bottom = 280.0
theme_override_constants/separation = 16

[node name="StartBtn" type="Button" parent="VBox"]
custom_minimum_size = Vector2(0, 60)
text = "Начать"

[node name="ContinueBtn" type="Button" parent="VBox"]
custom_minimum_size = Vector2(0, 60)
text = "Продолжить"

[node name="DeleteBtn" type="Button" parent="VBox"]
custom_minimum_size = Vector2(0, 40)
text = "Удалить сохранение"

[node name="QuitBtn" type="Button" parent="VBox"]
custom_minimum_size = Vector2(0, 60)
text = "Выход"

[connection signal="pressed" from="VBox/StartBtn" to="." method="_on_start_pressed"]
[connection signal="pressed" from="VBox/ContinueBtn" to="." method="_on_continue_pressed"]
[connection signal="pressed" from="VBox/DeleteBtn" to="." method="_on_delete_pressed"]
[connection signal="pressed" from="VBox/QuitBtn" to="." method="_on_quit_pressed"]
""")

# ============================================================
# TSCN — Player
# ============================================================
w("scenes/Player.tscn", """[gd_scene load_steps=4 format=3]
[ext_resource type="Script" path="res://scripts/PlayerController.gd" id="1"]

[sub_resource type="CapsuleShape3D" id="cs"]
radius = 0.35
height = 1.8

[sub_resource type="CapsuleMesh" id="cm"]
radius = 0.35
height = 1.8

[node name="Player" type="CharacterBody3D"]
script = ExtResource("1")

[node name="Collision" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)
shape = SubResource("cs")

[node name="Mesh" type="MeshInstance3D" parent="."]
visible = false
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)
mesh = SubResource("cm")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
current = true

[node name="RayCast3D" type="RayCast3D" parent="Camera3D"]
target_position = Vector3(0, 0, -3.5)
""")

# ============================================================
# TSCN — DialogueUI
# ============================================================
w("scenes/DialogueUI.tscn", """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/DialogueUI.gd" id="1"]

[node name="DialogueUI" type="CanvasLayer"]
layer = 10
script = ExtResource("1")

[node name="Panel" type="PanelContainer" parent="."]
visible = false
anchors_preset = 12
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = 60.0
offset_top = -240.0
offset_right = -60.0
offset_bottom = -40.0

[node name="VBox" type="VBoxContainer" parent="Panel"]
theme_override_constants/separation = 12

[node name="Speaker" type="Label" parent="Panel/VBox"]
theme_override_colors/font_color = Color(0.85, 0.3, 0.3, 1)
theme_override_font_sizes/font_size = 22
text = "?"

[node name="Text" type="Label" parent="Panel/VBox"]
custom_minimum_size = Vector2(0, 120)
theme_override_font_sizes/font_size = 20
text = "..."
autowrap_mode = 3

[node name="Hint" type="Label" parent="Panel/VBox"]
theme_override_colors/font_color = Color(0.55, 0.55, 0.55, 1)
theme_override_font_sizes/font_size = 16
text = "[E] далее"
horizontal_alignment = 2
""")

# ============================================================
# TSCN — SanitySystem
# ============================================================
w("scenes/SanitySystem.tscn", """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/SanitySystem.gd" id="1"]

[node name="SanitySystem" type="CanvasLayer"]
layer = 5
script = ExtResource("1")

[node name="Overlay" type="ColorRect" parent="."]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
mouse_filter = 2
color = Color(0.4, 0, 0, 0)
""")

# ============================================================
# TSCN — AnagramPuzzle
# ============================================================
w("scenes/AnagramPuzzle.tscn", """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/AnagramPuzzle.gd" id="1"]

[node name="AnagramPuzzle" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1")

[node name="Dim" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = Color(0, 0, 0, 0.7)

[node name="VBox" type="VBoxContainer" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -260.0
offset_top = -140.0
offset_right = 260.0
offset_bottom = 140.0
theme_override_constants/separation = 16

[node name="Title" type="Label" parent="VBox"]
theme_override_font_sizes/font_size = 32
text = "АНАГРАММА"
horizontal_alignment = 1

[node name="Hint" type="Label" parent="VBox"]
custom_minimum_size = Vector2(0, 60)
theme_override_font_sizes/font_size = 18
text = "..."
autowrap_mode = 3
horizontal_alignment = 1

[node name="Input" type="LineEdit" parent="VBox"]
custom_minimum_size = Vector2(0, 50)
placeholder_text = "введите ответ"

[node name="Buttons" type="HBoxContainer" parent="VBox"]
theme_override_constants/separation = 16

[node name="Submit" type="Button" parent="VBox/Buttons"]
custom_minimum_size = Vector2(0, 50)
size_flags_horizontal = 3
text = "Проверить"

[node name="Close" type="Button" parent="VBox/Buttons"]
custom_minimum_size = Vector2(0, 50)
size_flags_horizontal = 3
text = "Закрыть"
""")

# ============================================================
# TSCN — ClueInventory
# ============================================================
w("scenes/ClueInventory.tscn", """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/ClueInventory.gd" id="1"]

[node name="ClueInventory" type="CanvasLayer"]
layer = 8
script = ExtResource("1")

[node name="Panel" type="PanelContainer" parent="."]
visible = false
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = 200.0
offset_top = 100.0
offset_right = -200.0
offset_bottom = -100.0

[node name="Margin" type="MarginContainer" parent="Panel"]
theme_override_constants/margin_left = 20
theme_override_constants/margin_top = 20
theme_override_constants/margin_right = 20
theme_override_constants/margin_bottom = 20

[node name="VBox" type="VBoxContainer" parent="Panel/Margin"]
theme_override_constants/separation = 12

[node name="Title" type="Label" parent="Panel/Margin/VBox"]
theme_override_font_sizes/font_size = 28
text = "УЛИКИ"

[node name="Scroll" type="ScrollContainer" parent="Panel/Margin/VBox"]
size_flags_vertical = 3

[node name="List" type="VBoxContainer" parent="Panel/Margin/VBox/Scroll"]
size_flags_horizontal = 3
theme_override_constants/separation = 8
""")

# ============================================================
# TSCN — Катсцены
# ============================================================
def cutscene_tscn(name, frames, durations, ambient, next_scene, bg_color="Color(0.03, 0.04, 0.07, 1)", font_color="Color(0.85, 0.85, 0.9, 1)"):
    fr = ", ".join('"%s"' % f.replace('"', '\\"') for f in frames)
    du = ", ".join(str(d) for d in durations)
    return """[gd_scene load_steps=2 format=3]
[ext_resource type="Script" path="res://scripts/Cutscene.gd" id="1"]

[node name="{NAME}" type="Node3D"]
script = ExtResource("1")
frames = PackedStringArray({FR})
durations = PackedFloat32Array({DU})
ambient = "{AMB}"
next_scene = "{NEXT}"

[node name="BG" type="ColorRect" parent="."]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
color = {BG}

[node name="UI" type="Control" parent="."]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0

[node name="Center" type="CenterContainer" parent="UI"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0

[node name="Text" type="Label" parent="UI/Center"]
custom_minimum_size = Vector2(900, 200)
theme_override_colors/font_color = {FC}
theme_override_font_sizes/font_size = 32
text = ""
horizontal_alignment = 1
vertical_alignment = 1
autowrap_mode = 3

[node name="Bottom" type="HBoxContainer" parent="UI"]
anchors_preset = 12
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_top = -80.0

[node name="Subtitle" type="Label" parent="UI/Bottom"]
size_flags_horizontal = 3
theme_override_colors/font_color = Color(0.5, 0.5, 0.55, 1)
theme_override_font_sizes/font_size = 16
text = "ПРОБЕЛ — пропустить"
horizontal_alignment = 1
""".replace("{NAME}", name).replace("{FR}", fr).replace("{DU}", du)\
   .replace("{AMB}", ambient).replace("{NEXT}", next_scene)\
   .replace("{BG}", bg_color).replace("{FC}", font_color)

w("scenes/Cutscene_Intro.tscn", cutscene_tscn(
    "Cutscene_Intro",
    ["Сентябрь 1954 года.",
     "Паром идёт к острову Крутогор.",
     "Маршал Виктор Санин страдает от морской болезни.",
     "Стас Громов, новый напарник, молчит.",
     "На острове — лечебница «Затишье».",
     "Накануне бесследно исчезла пациентка Раиса Солова.",
     "Пробел — начать."],
    [2.5, 3.0, 3.5, 3.0, 3.0, 3.5, 3.0],
    "sea", "res://scenes/Act1_Ferry.tscn"))

w("scenes/Cutscene_Act2.tscn", cutscene_tscn(
    "Cutscene_Act2",
    ["Ворота «Затишья».",
     "У маршалов отбирают оружие.",
     "Доктор Ремизов встречает вас.",
     "Пропала пациентка. Комната заперта изнутри.",
     "Утром её не было. Замок — снаружи."],
    [2.5, 2.5, 3.0, 3.5, 3.5],
    "drone", "res://scenes/Act2_Asylum.tscn",
    "Color(0.05, 0.03, 0.03, 1)", "Color(0.85, 0.8, 0.8, 1)"))

w("scenes/Cutscene_Final.tscn", cutscene_tscn(
    "Cutscene_Final",
    ["Маяк. Верхний этаж.",
     "«Вы не Виктор Санин. Вы — Иван Кострин.»",
     "Алиса не погибла в пожаре.",
     "Она утопила троих детей. Вы застрелили её.",
     "Всё это — психодрама. Последний шанс перед лоботомией.",
     "Теперь выбор за вами."],
    [3.0, 4.0, 3.5, 4.0, 4.5, 3.0],
    "whisper", "res://scenes/Act5_Finale.tscn",
    "Color(0.02, 0.02, 0.02, 1)", "Color(0.9, 0.85, 0.85, 1)"))

# ============================================================
# Акты
# ============================================================
def act_scene(name, intro, ambient, npcs, exit_flag="", exit_target=-1):
    npc_blocks = ""
    for n in npcs:
        npc_blocks += """
[node name="{N}" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {X}, 1, {Z})
script = ExtResource("{S}")

[sub_resource type="BoxShape3D" id="bs_{N}"]
size = Vector3(1, 2, 1)

[node name="Collision" type="CollisionShape3D" parent="{N}"]
shape = SubResource("bs_{N}")
""".replace("{N}", n["name"]).replace("{X}", str(n["x"])).replace("{Z}", str(n["z"])).replace("{S}", n["script"])
        if "dialogue" in n:
            npc_blocks += 'dialogue_path = "%s"\n' % n["dialogue"]
        if "flag" in n:
            npc_blocks += 'sets_flag = "%s"\n' % n["flag"]
        if "clue" in n:
            npc_blocks += 'clue = "%s"\n' % n["clue"]
        if "target" in n:
            npc_blocks += 'target_word = "%s"\n' % n["target"]
        if "hint" in n:
            npc_blocks += 'hint_text = "%s"\n' % n["hint"]

    return """[gd_scene load_steps=10 format=3]
[ext_resource type="Script" path="res://scripts/ActController.gd" id="ac"]
[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="pl"]
[ext_resource type="Script" path="res://scripts/ExitTrigger.gd" id="ex"]
[ext_resource type="Script" path="res://scripts/Interactable.gd" id="in"]
[ext_resource type="Script" path="res://scripts/AnagramTrigger.gd" id="an"]

[sub_resource type="BoxShape3D" id="fs"]
size = Vector3(24, 0.4, 24)

[sub_resource type="BoxMesh" id="fm"]
size = Vector3(24, 0.4, 24)

[sub_resource type="BoxShape3D" id="ws"]
size = Vector3(24, 4, 0.5)

[sub_resource type="BoxMesh" id="wm"]
size = Vector3(24, 4, 0.5)

[node name="{NAME}" type="Node3D"]
script = ExtResource("ac")
intro_dialogue = "{INTRO}"
ambient = "{AMB}"

[node name="Floor" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -0.2, 0)
[node name="Collision" type="CollisionShape3D" parent="Floor"]
shape = SubResource("fs")
[node name="Mesh" type="MeshInstance3D" parent="Floor"]
mesh = SubResource("fm")

[node name="WallN" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, -12)
[node name="Collision" type="CollisionShape3D" parent="WallN"]
shape = SubResource("ws")
[node name="Mesh" type="MeshInstance3D" parent="WallN"]
mesh = SubResource("wm")

[node name="WallS" type="StaticBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 12)
[node name="Collision" type="CollisionShape3D" parent="WallS"]
shape = SubResource("ws")
[node name="Mesh" type="MeshInstance3D" parent="WallS"]
mesh = SubResource("wm")

[node name="WallE" type="StaticBody3D" parent="."]
transform = Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, 12, 2, 0)
[node name="Collision" type="CollisionShape3D" parent="WallE"]
shape = SubResource("ws")
[node name="Mesh" type="MeshInstance3D" parent="WallE"]
mesh = SubResource("wm")

[node name="WallW" type="StaticBody3D" parent="."]
transform = Transform3D(0, 0, 1, 0, 1, 0, -1, 0, 0, -12, 2, 0)
[node name="Collision" type="CollisionShape3D" parent="WallW"]
shape = SubResource("ws")
[node name="Mesh" type="MeshInstance3D" parent="WallW"]
mesh = SubResource("wm")

[node name="Player" parent="." instance=ExtResource("pl")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 8)

[node name="Exit" type="Area3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, -11)
script = ExtResource("ex")
requires_flag = "{RF}"
target_act = {TA}

[sub_resource type="BoxShape3D" id="exs"]
size = Vector3(4, 3, 1)

[node name="ExitCollision" type="CollisionShape3D" parent="Exit"]
shape = SubResource("exs")

{NPCS}
""".replace("{NAME}", name).replace("{INTRO}", intro).replace("{AMB}", ambient)\
   .replace("{RF}", exit_flag).replace("{TA}", str(exit_target))\
   .replace("{NPCS}", npc_blocks)

# Акт 1 — паром
w("scenes/Act1_Ferry.tscn", act_scene(
    "Act1_Ferry", "res://dialogues/act1_intro.json", "sea",
    [
        {"name": "Stan", "x": 3, "z": 0, "script": "in",
         "dialogue": "res://dialogues/act1_stan.json", "flag": "met_stan",
         "clue": "Стас уклончиво говорит о прошлом"},
        {"name": "Note1", "x": -4, "z": -3, "script": "in",
         "dialogue": "res://dialogues/act1_note.json",
         "clue": "Записка: комната была заперта изнутри и снаружи"},
    ],
    exit_flag="met_stan"))

# Акт 2 — холл (вход через катсцену)
w("scenes/Act2_Asylum.tscn", act_scene(
    "Act2_Asylum", "res://dialogues/act2_intro.json", "drone",
    [
        {"name": "Remizov", "x": 0, "z": -6, "script": "in",
         "dialogue": "res://dialogues/act2_remizov.json", "flag": "met_remizov",
         "clue": "Ремизов утверждает: пациентов 66, а не 67"},
        {"name": "RoomNote", "x": -8, "z": 0, "script": "in",
         "dialogue": "res://dialogues/act2_note.json",
         "clue": "Записка «ЗАКОНЫ» и «КТО 67?»"},
    ],
    exit_flag="met_remizov"))

# Акт 3 — корпус + анаграмма
w("scenes/Act3_Cell.tscn", act_scene(
    "Act3_Cell", "res://dialogues/act3_intro.json", "drone",
    [
        {"name": "Vetrov", "x": 0, "z": -6, "script": "in",
         "dialogue": "res://dialogues/act3_vetrov.json", "flag": "met_vetrov",
         "clue": "Ветров: «Мы все подопытные, особенно ты»"},
        {"name": "AnagramWall", "x": 8, "z": -10, "script": "an",
         "target": "ИВАН КОСТРИН",
         "hint": "Переставьте буквы: В И К Т О Р С А Н И Н"},
    ],
    exit_flag="puzzle_solved"))

# Акт 4 — маяк
w("scenes/Act4_Lighthouse.tscn", act_scene(
    "Act4_Lighthouse", "res://dialogues/act4_intro.json", "sea",
    [
        {"name": "TrueRaisa", "x": -4, "z": 0, "script": "in",
         "dialogue": "res://dialogues/act4_raisa.json", "flag": "met_true_raisa",
         "clue": "Настоящая Раиса считает себя медсестрой"},
        {"name": "WifeVision", "x": 6, "z": -4, "script": "in",
         "dialogue": "res://dialogues/act4_wife.json", "flag": "saw_wife",
         "clue": "Видение Алисы: «Почему ты меня убил?»"},
    ],
    exit_flag="met_true_raisa"))

# Акт 5 — финал
w("scenes/Act5_Finale.tscn", act_scene(
    "Act5_Finale", "res://dialogues/act5_intro.json", "whisper",
    [
        {"name": "Lesov", "x": 0, "z": -6, "script": "in",
         "dialogue": "res://dialogues/act5_finale.json", "flag": "finale_seen"},
    ],
    exit_flag="finale_seen", exit_target=99))

# ============================================================
# Диалоги
# ============================================================
dlg("dialogues/act1_intro.json", [
    {"speaker": "Санин", "text": "Паром качает. Голова раскалывается..."},
    {"speaker": "Стас", "text": "Держись, маршал. Скоро на месте."},
    {"speaker": "Санин", "text": "Ты новенький? Откуда?"},
    {"speaker": "Стас", "text": "Служил в Тихоморске, штат Озёрный."},
])
dlg("dialogues/act1_stan.json", [
    {"speaker": "Стас", "text": "Санин, ты как? Лицо серое."},
    {"speaker": "Санин", "text": "Мигрень. Таблетки не возьму."},
])
dlg("dialogues/act1_note.json", [
    {"speaker": "Записка", "text": "«Она заперлась изнутри. Утром комната заперта снаружи.»"},
    {"speaker": "Санин", "text": "Невозможно. Или кто-то врёт."},
])
dlg("dialogues/act2_intro.json", [
    {"speaker": "Ремизов", "text": "Добро пожаловать в «Затишье», маршал."},
    {"speaker": "Ремизов", "text": "Пропала пациентка Раиса Солова. Убийца трёх детей."},
])
dlg("dialogues/act2_remizov.json", [
    {"speaker": "Санин", "text": "Мне нужны списки пациентов. Все 67."},
    {"speaker": "Ремизов", "text": "Здесь 66 пациентов. Я не понимаю, о чём вы."},
])
dlg("dialogues/act2_note.json", [
    {"speaker": "Санин", "text": "«ЗАКОНЫ... КТО 67?...»"},
    {"speaker": "Голос", "text": "Правило четырёх. Считай."},
])
dlg("dialogues/act3_intro.json", [
    {"speaker": "Санин", "text": "Самый охраняемый корпус. Здесь прячут 67-го."},
])
dlg("dialogues/act3_vetrov.json", [
    {"speaker": "Ветров", "text": "Мой друг, кто есть ты?"},
    {"speaker": "Ветров", "text": "Верников предупреждал тебя. Ты забыл?"},
    {"speaker": "Ветров", "text": "Мы все здесь подопытные. Особенно ты."},
])
dlg("dialogues/act4_intro.json", [
    {"speaker": "Санин", "text": "Маяк. Здесь «центр экспериментов»."},
    {"speaker": "Алиса", "text": "Ты мне снишься. Ты должен проснуться."},
])
dlg("dialogues/act4_raisa.json", [
    {"speaker": "Раиса", "text": "Я медсестра. У меня муж и дети. Я не убийца."},
    {"speaker": "Санин", "text": "Это иллюзия. Ты — Раиса Солова."},
])
dlg("dialogues/act4_wife.json", [
    {"speaker": "Алиса", "text": "Почему ты меня убил?"},
    {"speaker": "Санин", "text": "Тебя убил Кострин. Не я."},
])
dlg("dialogues/act5_intro.json", [
    {"speaker": "Ремизов", "text": "Маршал Санин, довольно."},
    {"speaker": "Стас", "text": "Вы не Виктор Санин. Вы — Иван Кострин."},
    {"speaker": "Санин", "text": "Это бред."},
    {"speaker": "Стас", "text": "Алиса утопила троих детей. Вы застрелили её. Всё это — психодрама."},
])
dlg("dialogues/act5_finale.json", [
    {"speaker": "Иван", "text": "Меня зовут Иван Кострин. Я убил жену в 1952 году."},
    {"speaker": "Лесов", "text": "Сработало. Впервые за два года..."},
    {"speaker": "Иван", "text": "Что хуже — жить монстром или умереть хорошим человеком?"},
    {"speaker": "Лесов", "text": "Выбор за вами, Иван."},
])

# ============================================================
# Звуки (процедурные WAV)
# ============================================================
def gen_sea(dur=6.0):
    n = int(SR * dur); out = []; lp = 0.0
    for i in range(n):
        t = i / SR
        white = random.uniform(-1, 1)
        lp = lp * 0.92 + white * 0.08
        swell = 0.6 + 0.4 * math.sin(2 * math.pi * 0.15 * t)
        out.append(lp * swell * 0.6)
    return out

def gen_heartbeat(dur=2.0):
    n = int(SR * dur); out = [0.0] * n
    for start in [0.1, 0.25, 0.9, 1.05]:
        s = int(start * SR)
        for k in range(int(0.15 * SR)):
            if s + k >= n: break
            env = math.exp(-k / (0.03 * SR))
            f = 60.0 * math.exp(-k / (0.05 * SR)) + 30.0
            out[s + k] += math.sin(2 * math.pi * f * k / SR) * env * 0.7
    return out

def gen_step(dur=0.3):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-t * 25)
        out.append(random.uniform(-1, 1) * env * 0.3 + math.sin(2 * math.pi * 80 * t) * env * 0.5)
    return out

def gen_door(dur=1.5):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = math.sin(math.pi * t / dur)
        f = 180 + 120 * math.sin(2 * math.pi * 1.5 * t) + 60 * math.sin(2 * math.pi * 7 * t)
        saw = ((t * f) % 1.0) * 2 - 1
        out.append(saw * env * 0.35)
    return out

def gen_drone(dur=8.0):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t * 2) * min(1.0, (dur - t) * 2)
        a = math.sin(2 * math.pi * 55 * t) * 0.3
        b = math.sin(2 * math.pi * 82.5 * t) * 0.2
        out.append((a + b + random.uniform(-1, 1) * 0.05) * env)
    return out

def gen_whisper(dur=4.0):
    n = int(SR * dur); out = []
    for i in range(n):
        t = i / SR
        mod = (math.sin(2 * math.pi * 4 * t) + math.sin(2 * math.pi * 7.3 * t)) * 0.5
        env = max(0.0, mod) * min(1.0, t * 3) * min(1.0, (dur - t) * 3)
        out.append(random.uniform(-1, 1) * env * 0.15)
    return out

save_wav("audio/sea.wav", gen_sea(6.0))
save_wav("audio/heartbeat.wav", gen_heartbeat(2.0))
save_wav("audio/step.wav", gen_step(0.3))
save_wav("audio/door.wav", gen_door(1.5))
save_wav("audio/drone.wav", gen_drone(8.0))
save_wav("audio/whisper.wav", gen_whisper(4.0))

# ============================================================
print("\n" + "=" * 60)
print("  ГОТОВО. Откройте папку Zatishye в Godot 4.3+ и нажмите F5.")
print("=" * 60)