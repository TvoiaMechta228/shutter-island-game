extends Node

var ambient_player: AudioStreamPlayer
var voice_player: AudioStreamPlayer

func _ready() -> void:
	ambient_player = AudioStreamPlayer.new()
	ambient_player.volume_db = -15.0
	add_child(ambient_player)
	
	voice_player = AudioStreamPlayer.new()
	voice_player.volume_db = -5.0
	add_child(voice_player)

func play_ambient(kind: String) -> void:
	# Создаем простой шум моря кодом
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var data := PackedByteArray()
	for i in range(44100):
		var val := int(randf_range(-1.0, 1.0) * 3000.0)
		data.append(val & 0xFF)
		data.append((val >> 8) & 0xFF)
	wav.data = data
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	ambient_player.stream = wav
	ambient_player.play()

func play_voice() -> void:
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 22050
	var data := PackedByteArray()
	for i in range(1000):
		var t := float(i) / 22050.0
		var val := int(sin(t * 400.0 * PI * 2.0) * 5000.0 * exp(-t * 20.0))
		data.append(val & 0xFF)
		data.append((val >> 8) & 0xFF)
	wav.data = data
	voice_player.stream = wav
	voice_player.pitch_scale = randf_range(0.8, 1.2)
	voice_player.play()

func play_step() -> void:
	pass

func stop_all() -> void:
	ambient_player.stop()
