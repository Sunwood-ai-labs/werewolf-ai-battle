#!/usr/bin/env python3
"""
werewolf-ai-battle Godview CLI

神視点でゲーム全体を監視するCLIツール。
全てのチャットメッセージとプレイヤーの状態をリアルタイムで表示。
"""

import asyncio
import websockets
import json
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.live import Live
from rich.align import Align


class WerewolfGodview:
    """神視点クライアント"""

    def __init__(self, server_url: str = "ws://localhost:8765"):
        self.server_url = server_url
        self.console = Console()
        self.players = []
        self.messages = {
            "public": [],
            "werewolf": [],
            "moderator": [],
        }
        self.events = []
        self.current_channel = "public"

    def create_header(self) -> Panel:
        """ヘッダーを作成"""
        header_text = Text()
        header_text.append("🐺 ", style="bold red")
        header_text.append("WEREWOLF AI BATTLE", style="bold magenta")
        header_text.append(" - Godview", style="dim")

        return Panel(
            Align.center(header_text),
            style="bold black on magenta",
            height=2,
        )

    def create_player_table(self) -> Table:
        """プレイヤーテーブルを作成"""
        table = Table(
            title="プレイヤー一覧",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("ID", style="dim", width=4)
        table.add_column("名前", style="cyan")
        table.add_column("役職", style="yellow")
        table.add_column("状態", style="bold")

        for i, player in enumerate(self.players, 1):
            status = "🟢 生存" if player.get("is_alive", True) else "💀 死亡"
            status_style = "green" if player.get("is_alive", True) else "red"

            # 役職によって色を変える
            role = player.get("role", "unknown")
            if role == "werewolf":
                role_style = "bold red"
            elif role == "moderator":
                role_style = "bold blue"
            else:
                role_style = "white"

            table.add_row(
                str(i),
                player.get("name", "Unknown"),
                Text(role, style=role_style),
                Text(status, style=status_style),
            )

        return table

    def create_chat_panel(self) -> Panel:
        """チャットパネルを作成"""
        messages = self.messages.get(self.current_channel, [])

        if not messages:
            chat_text = Text(
                f"チャンネル: {self.current_channel}\nまだメッセージはありません",
                style="dim",
            )
        else:
            chat_text = Text()
            # 最新20件を表示（最新が下に来る）
            display_messages = messages[-20:]
            chat_text.append(f"チャンネル: {self.current_channel}  (最新{len(display_messages)}件)\n\n", style="bold dim")

            for msg in display_messages:
                timestamp = msg.get("timestamp", "")[-8:]
                player = msg.get("player", "Unknown")
                role = msg.get("role", "unknown")
                content = msg.get("content", "")

                # 役職に応じた色
                if role == "werewolf":
                    player_style = "red"
                elif role == "moderator":
                    player_style = "blue"
                else:
                    player_style = "cyan"

                chat_text.append(f"[{timestamp}] ", style="dim")
                chat_text.append(f"{player}: ", style=player_style)
                chat_text.append(f"{content}\n", style="white")

        return Panel(
            chat_text,
            title=f"[{self.current_channel}]",
            border_style="magenta",
            height=40,  # 高さを大きくする
        )

    def create_event_panel(self) -> Panel:
        """イベントパネルを作成"""
        if not self.events:
            event_text = Text("イベントはありません", style="dim")
        else:
            event_text = Text()
            for event in self.events[-3:]:  # 最新3件
                event_type = event.get("type", "")
                event_str = f"[{datetime.now().strftime('%H:%M:%S')}] {event_type}"
                event_text.append(event_str + "\n")

        return Panel(
            event_text,
            title="イベントログ",
            border_style="yellow",
            height=5,
        )

    def create_layout(self) -> Layout:
        """レイアウトを作成"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=2),
            Layout(name="main"),
            Layout(name="events", size=3),  # イベントログを小さく
        )

        layout["main"].split_row(
            Layout(name="players", ratio=1),
            Layout(name="chat", ratio=2),
        )

        layout["header"].update(self.create_header())
        layout["players"].update(Panel(self.create_player_table(), title="プレイヤー"))
        layout["chat"].update(self.create_chat_panel())
        layout["events"].update(self.create_event_panel())

        return layout

    def add_event(self, event: dict):
        """イベントを追加"""
        self.events.append(event)
        if len(self.events) > 20:
            self.events = self.events[-20:]

    async def handle_message(self, message: str):
        """サーバーからのメッセージを処理"""
        try:
            data = json.loads(message)

            if data.get("type") == "init":
                # 初期データ
                self.players = data.get("players", [])
                channels_data = data.get("channels", {})
                for channel_name, channel_info in channels_data.items():
                    self.messages[channel_name] = channel_info.get("messages", [])
                # デバッグログ
                self.console.print(f"[dim]プレイヤー数: {len(self.players)}, publicメッセージ数: {len(self.messages.get('public', []))}[/]")

            elif data.get("type") == "player_joined":
                # プレイヤー参加
                player = data.get("player", {})
                self.players.append(player)
                self.add_event({"type": f"🎮 {player.get('name')} が参加", "data": player})

            elif data.get("type") == "player_left":
                # プレイヤー退出
                player = data.get("player", {})
                self.players = [
                    p for p in self.players if p.get("id") != player.get("id")
                ]
                self.add_event({"type": f"👋 {player.get('name')} が退出", "data": player})

            elif data.get("type") == "channel_message":
                # チャンネルメッセージ
                channel = data.get("channel", "public")
                msg = data.get("message", {})
                if channel in self.messages:
                    self.messages[channel].append(msg)

        except json.JSONDecodeError:
            pass

    async def connect(self):
        """サーバーに接続"""
        self.console.print(
            f"[bold cyan]🐺 Godview に接続中... [/] {self.server_url}"
        )

        try:
            async with websockets.connect(self.server_url) as websocket:
                # 神視点として登録（パスワード付き）
                await websocket.send(json.dumps({"type": "godview", "password": "wolf"}))

                self.console.print("[bold green]✅ 接続成功！[/]")
                self.console.print("[dim]Ctrl+C で終了[/]")

                # Live Display開始
                with Live(console=self.console, refresh_per_second=10) as live:
                    async for message in websocket:
                        await self.handle_message(message)
                        live.update(self.create_layout())

        except ConnectionRefusedError:
            self.console.print(
                "[bold red]❌ 接続失敗。サーバーが起動しているか確認してください。[/]"
            )
        except Exception as e:
            self.console.print(f"[bold red]❌ エラー: {e}[/]")


async def main():
    """メイン関数"""
    godview = WerewolfGodview()
    await godview.connect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Godview を終了します")
