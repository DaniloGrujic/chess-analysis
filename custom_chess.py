import chess
import chess.pgn
import chess.svg
from IPython.display import SVG, display, clear_output, HTML
import ipywidgets as widgets
from ipywidgets import HBox, VBox
import io


class ChessGame:
	def __init__(self, player_name, df_term_moves, df_game_info):
		self.player_name = player_name
		self.board = chess.Board()
		self.moves_sequence = None
		self.output = widgets.Output()
		self.notation = None
		self.moves_played = []
		self.term_moves = df_term_moves
		self.game_info = df_game_info
		self.flipped = False
		self.selected_game_idx = None

	def display_board(self):
		with self.output:
			clear_output(wait=True)
			display(SVG(chess.svg.board(board=self.board, size=500, flipped=self.flipped)))

	def handle_next_move(self, next_button, previous_button, termination_label):
		with self.output:
			move = self.moves_sequence.pop(0)
			self.moves_played.append(move)
			self.board.push(move)
			self.display_board()

			# Buttons state
			next_button = next_button
			previous_button = previous_button

			if len(self.moves_sequence) != len(self.notation):
				previous_button.disabled = False
			if len(self.moves_sequence) == 0:
				next_button.disabled = True
				termination_label.value = self.term_moves.iloc[self.selected_game_idx, 0]

	def handle_previous_move(self, next_button, previous_button):
		# Buttons state
		next_button = next_button
		next_button.disabled = False
		previous_button = previous_button

		with self.output:
			if self.moves_played:
				move = self.moves_played.pop(-1)
				self.moves_sequence.insert(0, move)
				try:
					self.board.pop()
					self.display_board()
				except Exception as e:
					print(f"Error: {e}")
		# else:
		#     print("No more moves in the sequence.")

		if len(self.moves_sequence) == len(self.notation):
			previous_button.disabled = True

	def restart_game(self, next_button, previous_button, termination_label):
		# Widget state
		next_button.disabled = False
		previous_button.disabled = True
		termination_label.value = ''

		with self.output:
			self.moves_sequence = self.notation.copy()
			self.board.reset()
			self.move = None
			self.display_board()

	def select_game(self, selected_game_idx, next_button, previous_button, termination_label, opponent_label):
		with self.output:
			self.selected_game_idx = selected_game_idx
			mainline = self.term_moves.iloc[self.selected_game_idx, 1]
			pgn = io.StringIO(mainline)
			game_pgn = chess.pgn.read_game(pgn)

			if self.game_info.iloc[selected_game_idx, 0] == self.player_name:
				self.flipped = False
				opponent_label.value = self.game_info.iloc[selected_game_idx, 3]

			elif self.game_info.iloc[selected_game_idx, 3] == self.player_name:
				self.flipped = True
				opponent_label.value = self.game_info.iloc[selected_game_idx, 0]

			self.notation = list(game_pgn.mainline_moves())
			self.moves_sequence = self.notation.copy()
			self.restart_game(next_button, previous_button, termination_label)


class UI:
	def __init__(self, player_name, game, game_info_cleaned):
		# Widgets
		self.opponent_label = widgets.Label()
		self.player_label = widgets.Label(value=f"{player_name}")
		self.termination_label = widgets.Label(value='')

		self.next_button = widgets.Button(description="", icon='arrow-right')
		self.next_button.on_click(lambda _: game.handle_next_move(
			self.next_button,
			self.previous_button,
			self.termination_label))

		self.previous_button = widgets.Button(description="", disabled=True, icon='arrow-left')
		self.previous_button.on_click(lambda _: game.handle_previous_move(self.next_button, self.previous_button))

		self.restart_button = widgets.Button(description="Restart Game")
		self.restart_button.on_click(lambda _: game.restart_game(
			self.next_button,
			self.previous_button,
			self.termination_label))

		self.select_button = widgets.Button(description="Select game", disabled=False, icon='chess-board')
		self.select_button.on_click(lambda _: game.select_game(
			self.select_box.index,
			self.next_button,
			self.previous_button,
			self.termination_label,
			self.opponent_label))

		self.select_box = widgets.Select(options=game_info_cleaned,
										 rows=12,
										 disabled=False)
		self.select_box.layout.width = '500px'

		game.select_game(self.select_box.index, self.next_button, self.previous_button, self.termination_label, self.opponent_label)
		self.display_widgets(game.output)

	def display_widgets(self, output):
		custom_style = HTML('''
		<style>
			.widget-select option { margin-bottom: 15px; }
			.widget-select option { font-size: 16px; }
			.widget-select option { padding-left: 20px; }
		</style>
		''')

		# Display the initial chess board with a UI
		restart_select_hbox = HBox([self.restart_button, self.select_button])
		previous_next_hbox = HBox([self.previous_button, self.next_button])
		v_box = VBox([restart_select_hbox, self.select_box, previous_next_hbox, self.termination_label])
		combined_widgets = HBox([output, v_box])

		display(custom_style)
		display(self.opponent_label)
		display(combined_widgets)
		display(self.player_label)
