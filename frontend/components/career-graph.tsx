import React, { useMemo } from "react";
import ReactFlow, { Controls, MiniMap } from "react-flow-renderer";

export default function CareerGraph({ score = 0, alternatives = [] }: { score?: number; alternatives?: any[] }) {
  const nodes = useMemo(() => {
    const center = { id: "you", data: { label: `You — ${score}%` }, position: { x: 250, y: 150 }, style: { background: "#4f46e5", color: "#fff", padding: 8, borderRadius: 8 } };
    const goal = { id: "goal", data: { label: "Goal Role (100%)" }, position: { x: 650, y: 150 }, style: { background: "#10b981", color: "#fff", padding: 8, borderRadius: 8 } };
    const altNodes = alternatives.slice(0, 6).map((a: any, i: number) => ({
      id: `alt-${i}`,
      data: { label: `${a.role_name} (${a.overlap_percent}%)` },
      position: { x: 250 + (i % 3) * 160, y: 350 + Math.floor(i / 3) * 120 },
      style: { background: "#f97316", color: "#fff", padding: 8, borderRadius: 8 },
    }));
    return [center, goal, ...altNodes];
  }, [score, alternatives]);

  const edges = useMemo(() => {
    const base = [{ id: "e-you-goal", source: "you", target: "goal", animated: true }];
    const alt = alternatives.slice(0, 6).map((a: any, i: number) => ({ id: `e-you-alt-${i}`, source: "you", target: `alt-${i}` }));
    return [...base, ...alt];
  }, [alternatives]);

  return (
    <section style={{ maxWidth: 980, margin: "20px auto", padding: 12 }}>
      <h2>Career Visualization</h2>

      <div style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            <strong>Progress to goal</strong>
            <div style={{ background: "#eef2ff", height: 12, borderRadius: 8, width: 480, marginTop: 8 }}>
              <div style={{ width: `${score}%`, height: "100%", background: "#4f46e5", borderRadius: 8 }} />
            </div>
          </div>
          <div style={{ minWidth: 140, textAlign: "right" }}>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{score}%</div>
            <div style={{ color: "#6b7280", fontSize: 13 }}>Current Standing</div>
          </div>
        </div>
      </div>

      <div style={{ height: 520, background: "#fff", borderRadius: 8, padding: 8 }}>
        <ReactFlow nodes={nodes} edges={edges} fitView style={{ background: "#fcfcff", borderRadius: 8 }}>
          <MiniMap />
          <Controls />
        </ReactFlow>
      </div>
    </section>
  );
}