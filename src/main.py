#!/usr/bin/env python3
"""
NEMESIS - AI-Powered Adaptive Boss Battle
Main entry point
"""
import argparse
import curses
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game.game_engine import GameEngine
from src.rendering.themes import THEMES

def main():
    parser = argparse.ArgumentParser(
        description="NEMESIS - AI-Powered Adaptive Boss Battle"
    )
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="neo",
        help="Visual theme"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI (classic mode)"
    )
    parser.add_argument(
        "--mode",
        choices=["normal", "boss"],
        default="normal",
        help="Game mode: normal (waves) or boss (boss fight)"
    )
    
    args = parser.parse_args()
    
    print("🎮 NEMESIS - AI-Powered Adaptive Boss Battle")
    print("=" * 50)
    
    if not args.no_ai:
        print("🧠 AI System: ENABLED")
        print("   The boss will learn from your playstyle...")
    else:
        print("🎮 Classic Mode: AI Disabled")
    
    print(f"🎨 Theme: {args.theme}")
    print(f"🎯 Mode: {args.mode}")
    print("\nStarting game...")
    print("=" * 50)
    
    try:
        engine = GameEngine(
            theme=args.theme,
            use_ai=not args.no_ai,
            mode=args.mode
        )
        curses.wrapper(engine.run)
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎮 Game Over!")
    print("=" * 50)

if __name__ == "__main__":
    main()
