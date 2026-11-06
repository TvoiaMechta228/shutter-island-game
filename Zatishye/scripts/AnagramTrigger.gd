extends StaticBody3D

@export var target_word: String = "ИВАН КОСТРИН"
@export var hint_text: String = "Переставьте буквы: В И К Т О Р С А Н И Н"

func interact() -> void:
	if GameManager.get_flag("puzzle_solved"): return
	AnagramPuzzle.solved.connect(_on_solved, CONNECT_ONE_SHOT)
	AnagramPuzzle.open(target_word, hint_text)

func _on_solved() -> void:
	GameManager.set_flag("puzzle_solved", true)
	GameManager.add_clue("Анаграмма разгадана: ИВАН КОСТРИН")
