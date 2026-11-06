extends Control

@onready var cont: Button = $VBox/ContinueBtn
@onready var dele: Button = $VBox/DeleteBtn

func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	if has_node("/root/AudioManager"):
		AudioManager.play_ambient("sea")
	cont.disabled = not SaveSystem.has_save()
	dele.disabled = not SaveSystem.has_save()
	# На случай, если сигналы в .tscn не прописались — подключаем вручную
	if not $VBox/StartBtn.pressed.is_connected(_on_start_pressed):
		$VBox/StartBtn.pressed.connect(_on_start_pressed)
	if not $VBox/ContinueBtn.pressed.is_connected(_on_continue_pressed):
		$VBox/ContinueBtn.pressed.connect(_on_continue_pressed)
	if not $VBox/DeleteBtn.pressed.is_connected(_on_delete_pressed):
		$VBox/DeleteBtn.pressed.connect(_on_delete_pressed)
	if not $VBox/QuitBtn.pressed.is_connected(_on_quit_pressed):
		$VBox/QuitBtn.pressed.connect(_on_quit_pressed)

func _on_start_pressed() -> void:
	GameManager.flags.clear()
	GameManager.clues.clear()
	get_tree().change_scene_to_file("res://scenes/Cutscene_Intro.tscn")

func _on_continue_pressed() -> void:
	SaveSystem.load_game()

func _on_delete_pressed() -> void:
	SaveSystem.delete_save()
	cont.disabled = true
	dele.disabled = true

func _on_quit_pressed() -> void:
	get_tree().quit()
