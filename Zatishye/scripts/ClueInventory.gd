extends CanvasLayer

@onready var panel: PanelContainer = $Panel
@onready var list: VBoxContainer = $Panel/Margin/VBox/Scroll/List
@onready var title: Label = $Panel/Margin/VBox/Title
var _open: bool = false

func _ready() -> void:
	panel.hide()
	process_mode = Node.PROCESS_MODE_ALWAYS

func toggle() -> void:
	if _open:
		_close()
	else:
		open()

func open() -> void:
	refresh()
	panel.show()
	_open = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().paused = true

func _close() -> void:
	panel.hide()
	_open = false
	get_tree().paused = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func refresh() -> void:
	if not is_inside_tree(): return
	for c in list.get_children(): c.queue_free()
	title.text = "УЛИКИ (%d)" % GameManager.clues.size()
	if GameManager.clues.is_empty():
		var l := Label.new(); l.text = "Пока ничего."; list.add_child(l); return
	for c in GameManager.clues:
		var l := Label.new()
		l.text = "• " + str(c)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		list.add_child(l)
