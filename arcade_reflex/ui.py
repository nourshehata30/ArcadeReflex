"""Tkinter touchscreen-style interface for ArcadeReflex."""

from random import Random
import tkinter as tk
from tkinter import messagebox, ttk

from arcade_reflex.config import (
    COLOURS,
    DATABASE_PATH,
    TELEMETRY_PATH,
    WINDOW_SIZE,
    WINDOW_TITLE,
)
from arcade_reflex.database import HighScoreRepository
from arcade_reflex.game import GameEngine, GameNotRunningError
from arcade_reflex.models import DIFFICULTIES, GameStatus
from arcade_reflex.telemetry import TelemetryLogger


class ArcadeReflexApp:
    """Coordinate the UI, game engine, database and telemetry services."""

    TARGET_WIDTH = 150
    TARGET_HEIGHT = 90
    EDGE_PADDING = 18

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(820, 620)
        self.root.configure(bg=COLOURS["background"])
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self.repository = HighScoreRepository(DATABASE_PATH)
        self.repository.initialise()
        self.telemetry = TelemetryLogger(TELEMETRY_PATH)
        self.random = Random()

        self.engine: GameEngine | None = None
        self.timer_job: str | None = None
        self.target_job: str | None = None

        self.player_name = tk.StringVar(value="Player 1")
        self.difficulty_name = tk.StringVar(value="Normal")
        self.score_text = tk.StringVar(value="Score: 0")
        self.timer_text = tk.StringVar(value="Time: 30.0")
        self.accuracy_text = tk.StringVar(value="Accuracy: 0.0%")

        self._configure_styles()
        self._build_home_screen()
        self._build_game_screen()
        self._show_home_screen()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "Arcade.TCombobox",
            fieldbackground=COLOURS["panel"],
            background=COLOURS["panel"],
            foreground=COLOURS["text"],
            arrowcolor=COLOURS["text"],
            padding=8,
        )
        style.configure(
            "Scores.Treeview",
            background=COLOURS["panel"],
            fieldbackground=COLOURS["panel"],
            foreground=COLOURS["text"],
            rowheight=28,
            borderwidth=0,
        )
        style.configure(
            "Scores.Treeview.Heading",
            background=COLOURS["accent"],
            foreground=COLOURS["background"],
            font=("Arial", 10, "bold"),
        )
        style.map("Scores.Treeview", background=[("selected", "#26385F")])

    def _build_home_screen(self) -> None:
        self.home_frame = tk.Frame(self.root, bg=COLOURS["background"])

        tk.Label(
            self.home_frame,
            text="ARCADE REFLEX",
            font=("Arial", 34, "bold"),
            fg=COLOURS["accent"],
            bg=COLOURS["background"],
        ).pack(pady=(30, 4))
        tk.Label(
            self.home_frame,
            text="A touchscreen-style reaction game",
            font=("Arial", 13),
            fg=COLOURS["muted"],
            bg=COLOURS["background"],
        ).pack(pady=(0, 24))

        controls = tk.Frame(self.home_frame, bg=COLOURS["panel"], padx=28, pady=22)
        controls.pack(fill="x", padx=90)

        self._add_control_label(controls, "Player name")
        tk.Entry(
            controls,
            textvariable=self.player_name,
            font=("Arial", 14),
            bg="#F7F9FC",
            fg="#111827",
            relief="flat",
        ).pack(fill="x", ipady=9, pady=(4, 14))

        self._add_control_label(controls, "Difficulty")
        difficulty_picker = ttk.Combobox(
            controls,
            textvariable=self.difficulty_name,
            values=[difficulty.name for difficulty in DIFFICULTIES.values()],
            state="readonly",
            style="Arcade.TCombobox",
            font=("Arial", 13),
        )
        difficulty_picker.pack(fill="x", pady=(4, 18))

        self._make_button(
            controls,
            text="START GAME",
            command=self._start_game,
            background=COLOURS["accent"],
            active_background=COLOURS["accent_hover"],
            foreground=COLOURS["background"],
        ).pack(fill="x", ipady=10)

        tk.Label(
            self.home_frame,
            text="HIGH SCORES",
            font=("Arial", 15, "bold"),
            fg=COLOURS["text"],
            bg=COLOURS["background"],
        ).pack(pady=(24, 8))

        columns = ("player", "difficulty", "score", "accuracy")
        self.score_table = ttk.Treeview(
            self.home_frame,
            columns=columns,
            show="headings",
            height=6,
            style="Scores.Treeview",
        )
        for column, heading, width in (
            ("player", "Player", 220),
            ("difficulty", "Difficulty", 120),
            ("score", "Score", 90),
            ("accuracy", "Accuracy", 110),
        ):
            self.score_table.heading(column, text=heading)
            self.score_table.column(column, width=width, anchor="center")
        self.score_table.pack(fill="x", padx=90)

    def _build_game_screen(self) -> None:
        self.game_frame = tk.Frame(self.root, bg=COLOURS["background"])

        stats = tk.Frame(self.game_frame, bg=COLOURS["panel"], pady=12)
        stats.pack(fill="x")
        for variable in (self.score_text, self.timer_text, self.accuracy_text):
            tk.Label(
                stats,
                textvariable=variable,
                font=("Arial", 15, "bold"),
                fg=COLOURS["text"],
                bg=COLOURS["panel"],
                width=20,
            ).pack(side="left", expand=True)

        self.playfield = tk.Frame(
            self.game_frame,
            bg="#10182B",
            highlightbackground="#2A3859",
            highlightthickness=2,
        )
        self.playfield.pack(fill="both", expand=True, padx=24, pady=24)

        self.target_button = self._make_button(
            self.playfield,
            text="TAP!",
            command=self._register_hit,
            background=COLOURS["target"],
            active_background=COLOURS["target_active"],
            foreground=COLOURS["text"],
            font=("Arial", 18, "bold"),
        )

        self._make_button(
            self.game_frame,
            text="END SESSION",
            command=self._finish_game,
            background=COLOURS["panel"],
            active_background="#26385F",
            foreground=COLOURS["text"],
            font=("Arial", 11, "bold"),
        ).pack(pady=(0, 18), ipadx=18, ipady=6)

    def _add_control_label(self, parent: tk.Widget, text: str) -> None:
        tk.Label(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            fg=COLOURS["muted"],
            bg=COLOURS["panel"],
            anchor="w",
        ).pack(fill="x")

    def _make_button(
        self,
        parent: tk.Widget,
        *,
        text: str,
        command: object,
        background: str,
        active_background: str,
        foreground: str,
        font: tuple[str, int, str] = ("Arial", 14, "bold"),
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            bg=background,
            activebackground=active_background,
            fg=foreground,
            activeforeground=foreground,
            relief="flat",
            cursor="hand2",
            bd=0,
        )

    def _start_game(self) -> None:
        name = self.player_name.get().strip()
        if not name:
            messagebox.showwarning("Player name", "Enter a player name to start.")
            return

        difficulty_key = self.difficulty_name.get().lower()
        self.engine = GameEngine(DIFFICULTIES[difficulty_key])
        self.engine.start(name)
        self.telemetry.log(
            "session_started",
            player=name,
            difficulty=self.engine.difficulty.name,
        )
        self._show_game_screen()
        self._update_stats()
        self.root.after(80, self._move_target)
        self._schedule_timer_tick()

    def _register_hit(self) -> None:
        if self.engine is None:
            return
        try:
            points = self.engine.register_hit()
        except GameNotRunningError:
            return

        self.telemetry.log(
            "target_hit",
            points=points,
            score=self.engine.score,
            hits=self.engine.hits,
        )
        self._cancel_target_job()
        self._move_target()
        self._update_stats()

    def _target_expired(self) -> None:
        self.target_job = None
        if self.engine is None or self.engine.status is not GameStatus.RUNNING:
            return
        try:
            penalty = self.engine.register_miss()
        except GameNotRunningError:
            self._finish_game()
            return

        self.telemetry.log(
            "target_missed",
            penalty=penalty,
            score=self.engine.score,
            misses=self.engine.misses,
        )
        self._move_target()
        self._update_stats()

    def _move_target(self) -> None:
        if self.engine is None or self.engine.status is not GameStatus.RUNNING:
            return

        self.playfield.update_idletasks()
        max_x = max(
            self.EDGE_PADDING,
            self.playfield.winfo_width() - self.TARGET_WIDTH - self.EDGE_PADDING,
        )
        max_y = max(
            self.EDGE_PADDING,
            self.playfield.winfo_height() - self.TARGET_HEIGHT - self.EDGE_PADDING,
        )
        x = self.random.randint(self.EDGE_PADDING, max_x)
        y = self.random.randint(self.EDGE_PADDING, max_y)
        self.target_button.place(
            x=x,
            y=y,
            width=self.TARGET_WIDTH,
            height=self.TARGET_HEIGHT,
        )
        self.target_job = self.root.after(
            self.engine.difficulty.target_interval_ms,
            self._target_expired,
        )

    def _schedule_timer_tick(self) -> None:
        self.timer_job = self.root.after(100, self._timer_tick)

    def _timer_tick(self) -> None:
        self.timer_job = None
        if self.engine is None or self.engine.status is not GameStatus.RUNNING:
            return
        self._update_stats()
        if self.engine.is_time_up():
            self._finish_game()
            return
        self._schedule_timer_tick()

    def _update_stats(self) -> None:
        if self.engine is None:
            return
        self.score_text.set(f"Score: {self.engine.score}")
        self.timer_text.set(f"Time: {self.engine.time_remaining:.1f}")
        self.accuracy_text.set(f"Accuracy: {self.engine.accuracy:.1f}%")

    def _finish_game(self) -> None:
        if self.engine is None or self.engine.status is GameStatus.IDLE:
            return

        self._cancel_jobs()
        result = self.engine.finish()
        self.repository.save_result(result)
        self.telemetry.log(
            "session_finished",
            player=result.player_name,
            difficulty=result.difficulty,
            score=result.score,
            hits=result.hits,
            misses=result.misses,
            accuracy=result.accuracy,
            duration_seconds=result.duration_seconds,
        )
        messagebox.showinfo(
            "Session complete",
            (
                f"Score: {result.score}\n"
                f"Hits: {result.hits}\n"
                f"Misses: {result.misses}\n"
                f"Accuracy: {result.accuracy:.1f}%"
            ),
        )
        self._show_home_screen()

    def _refresh_scores(self) -> None:
        for item_id in self.score_table.get_children():
            self.score_table.delete(item_id)
        for score in self.repository.top_scores(8):
            self.score_table.insert(
                "",
                "end",
                values=(
                    score.player_name,
                    score.difficulty,
                    score.score,
                    f"{score.accuracy:.1f}%",
                ),
            )

    def _show_home_screen(self) -> None:
        self._cancel_jobs()
        self.target_button.place_forget()
        self.game_frame.pack_forget()
        self.home_frame.pack(fill="both", expand=True)
        self._refresh_scores()

    def _show_game_screen(self) -> None:
        self.home_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)

    def _cancel_target_job(self) -> None:
        if self.target_job is not None:
            self.root.after_cancel(self.target_job)
            self.target_job = None

    def _cancel_jobs(self) -> None:
        self._cancel_target_job()
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def _close(self) -> None:
        self._cancel_jobs()
        if self.engine is not None and self.engine.status is GameStatus.RUNNING:
            self.telemetry.log(
                "session_abandoned",
                player=self.engine.player_name,
                score=self.engine.score,
            )
        self.root.destroy()


def main() -> None:
    """Create the Tk root window and start the event loop."""

    root = tk.Tk()
    ArcadeReflexApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

