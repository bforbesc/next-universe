"use client";

/**
 * The 2D world map: one renderer for the "mission-map-2d" game format.
 * Mission nodes sit along a path; the player walks with the arrow keys and
 * presses SPACE at an unlocked node to enter the mission. All art is generated
 * (no assets) so any theme can recolor the world.
 */
import { useEffect, useRef } from "react";

export interface MapNode {
  missionId: string;
  title: string;
  status: "locked" | "available" | "completed";
}

const THEME_STYLES: Record<string, { bg: number; path: number; player: number; accent: number }> = {
  space: { bg: 0x0b1026, path: 0x2c3566, player: 0x9ecbff, accent: 0x7c5cff },
  football: { bg: 0x0a3d1f, path: 0x1e6b3a, player: 0xffffff, accent: 0xffd166 },
  music: { bg: 0x250a3d, path: 0x4a1f6b, player: 0xff9ecb, accent: 0x4ecdc4 },
  explorer: { bg: 0x0a2d3d, path: 0x1f5b6b, player: 0xffe29e, accent: 0x4ecdc4 },
};

const WIDTH = 1040;
const HEIGHT = 380;

interface Props {
  theme: string;
  nodes: MapNode[];
  onEnterMission: (missionId: string) => void;
}

export default function GameCanvas({ theme, nodes, onEnterMission }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const enterRef = useRef(onEnterMission);
  enterRef.current = onEnterMission;

  useEffect(() => {
    let game: import("phaser").Game | null = null;
    let cancelled = false;

    (async () => {
      const Phaser = (await import("phaser")).default;
      if (cancelled || !hostRef.current) return;

      const style = THEME_STYLES[theme] ?? THEME_STYLES.explorer;

      class MapScene extends Phaser.Scene {
        private player!: import("phaser").GameObjects.Arc;
        private cursors!: import("phaser").Types.Input.Keyboard.CursorKeys;
        private spaceKey!: import("phaser").Input.Keyboard.Key;
        private prompt!: import("phaser").GameObjects.Text;
        private nodePositions: { x: number; y: number; node: MapNode }[] = [];

        create() {
          this.cameras.main.setBackgroundColor(style.bg);

          // ambient dots (stars / crowd / lights / fireflies)
          for (let i = 0; i < 70; i++) {
            const dot = this.add.circle(
              Phaser.Math.Between(0, WIDTH),
              Phaser.Math.Between(0, HEIGHT),
              Phaser.Math.Between(1, 2),
              0xffffff,
              Phaser.Math.FloatBetween(0.15, 0.5),
            );
            this.tweens.add({
              targets: dot,
              alpha: 0.05,
              duration: Phaser.Math.Between(1200, 3200),
              yoyo: true,
              repeat: -1,
            });
          }

          // path through the nodes
          const margin = 140;
          const step = nodes.length > 1 ? (WIDTH - margin * 2) / (nodes.length - 1) : 0;
          this.nodePositions = nodes.map((node, i) => ({
            x: margin + step * i,
            y: HEIGHT / 2 + (i % 2 === 0 ? 40 : -40),
            node,
          }));

          const path = this.add.graphics();
          path.lineStyle(6, style.path, 1);
          path.beginPath();
          this.nodePositions.forEach((p, i) => {
            if (i === 0) path.moveTo(p.x, p.y);
            else path.lineTo(p.x, p.y);
          });
          path.strokePath();

          // mission nodes
          this.nodePositions.forEach((p, i) => {
            const color =
              p.node.status === "completed"
                ? 0x3fb950
                : p.node.status === "available"
                  ? style.accent
                  : 0x4a5168;
            const circle = this.add.circle(p.x, p.y, 22, color);
            circle.setStrokeStyle(3, 0xffffff, p.node.status === "locked" ? 0.15 : 0.6);
            if (p.node.status === "available") {
              this.tweens.add({
                targets: circle,
                scale: 1.18,
                duration: 700,
                yoyo: true,
                repeat: -1,
                ease: "Sine.easeInOut",
              });
            }
            const label = p.node.status === "locked" ? "???" : p.node.title;
            this.add
              .text(p.x, p.y + 40, `${i + 1}. ${label}`, {
                fontSize: "13px",
                color: p.node.status === "locked" ? "#6a7186" : "#e6e8ee",
                align: "center",
                wordWrap: { width: 170 },
              })
              .setOrigin(0.5, 0);
            if (p.node.status === "completed") {
              this.add.text(p.x - 7, p.y - 9, "✓", { fontSize: "18px", color: "#ffffff" });
            }
          });

          // player
          const start = this.nodePositions[0];
          this.player = this.add.circle(start.x - 70, start.y - 40, 12, style.player);
          this.player.setStrokeStyle(2, 0xffffff, 0.8);

          this.prompt = this.add
            .text(0, 0, "", { fontSize: "14px", color: "#ffffff", backgroundColor: "#000000aa", padding: { x: 8, y: 4 } })
            .setOrigin(0.5, 1)
            .setVisible(false);

          this.cursors = this.input.keyboard!.createCursorKeys();
          this.spaceKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

          // click/tap fallback: clicking an unlocked node enters it directly
          this.nodePositions.forEach((p) => {
            if (p.node.status === "locked") return;
            const zone = this.add.zone(p.x, p.y, 60, 60).setInteractive({ useHandCursor: true });
            zone.on("pointerdown", () => enterRef.current(p.node.missionId));
          });
        }

        update() {
          const speed = 4;
          if (this.cursors.left.isDown) this.player.x -= speed;
          if (this.cursors.right.isDown) this.player.x += speed;
          if (this.cursors.up.isDown) this.player.y -= speed;
          if (this.cursors.down.isDown) this.player.y += speed;
          this.player.x = Phaser.Math.Clamp(this.player.x, 12, WIDTH - 12);
          this.player.y = Phaser.Math.Clamp(this.player.y, 12, HEIGHT - 12);

          const near = this.nodePositions.find(
            (p) => Phaser.Math.Distance.Between(this.player.x, this.player.y, p.x, p.y) < 48,
          );
          if (near && near.node.status !== "locked") {
            this.prompt
              .setText(
                near.node.status === "completed"
                  ? "press SPACE to replay"
                  : "press SPACE to start mission",
              )
              .setPosition(near.x, near.y - 32)
              .setVisible(true);
            if (Phaser.Input.Keyboard.JustDown(this.spaceKey)) {
              enterRef.current(near.node.missionId);
            }
          } else {
            this.prompt.setVisible(false);
          }
        }
      }

      game = new Phaser.Game({
        type: Phaser.AUTO,
        parent: hostRef.current,
        width: WIDTH,
        height: HEIGHT,
        scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
        scene: MapScene,
      });
    })();

    return () => {
      cancelled = true;
      game?.destroy(true);
    };
    // re-create the scene whenever progress changes the node statuses
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, JSON.stringify(nodes.map((n) => n.status))]);

  return <div ref={hostRef} className="game-wrap" />;
}
