"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createAdventure, createStudent } from "@/lib/api";
import type { StudentProfileIn } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const profile: StudentProfileIn = {
      name: String(form.get("name") || "").trim(),
      age: form.get("age") ? Number(form.get("age")) : null,
      interests: String(form.get("interests") || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .slice(0, 10),
      prior_knowledge: form.get("prior_knowledge") as StudentProfileIn["prior_knowledge"],
      preferred_theme: String(form.get("preferred_theme") || "") || null,
      learning_goal: String(form.get("learning_goal") || "") || null,
      difficulty_preference: form.get(
        "difficulty_preference",
      ) as StudentProfileIn["difficulty_preference"],
    };

    setBusy(true);
    setError("");
    try {
      setStatus("Creating your profile…");
      const student = await createStudent(profile);
      setStatus("Building your world… (the AI is writing your story)");
      const adventure = await createAdventure(student.id);
      router.push(`/play/${adventure.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
      setStatus("");
    }
  }

  return (
    <main className="container">
      <h1>Next Universe</h1>
      <p className="subtitle">
        Tell us about yourself — we&apos;ll build a world where learning Python is the
        adventure.
      </p>

      <form className="card form-grid" onSubmit={onSubmit}>
        <div>
          <label htmlFor="name">Your name *</label>
          <input id="name" name="name" required maxLength={80} placeholder="Ada" />
        </div>
        <div>
          <label htmlFor="age">Age</label>
          <input id="age" name="age" type="number" min={5} max={120} placeholder="12" />
        </div>
        <div className="full">
          <label htmlFor="interests">What do you love? (comma-separated)</label>
          <input
            id="interests"
            name="interests"
            placeholder="space, football, music…"
          />
        </div>
        <div>
          <label htmlFor="prior_knowledge">Programming experience</label>
          <select id="prior_knowledge" name="prior_knowledge" defaultValue="none">
            <option value="none">Complete beginner</option>
            <option value="some">I&apos;ve tried a little</option>
            <option value="comfortable">Comfortable with basics</option>
          </select>
        </div>
        <div>
          <label htmlFor="difficulty_preference">Challenge level</label>
          <select
            id="difficulty_preference"
            name="difficulty_preference"
            defaultValue="standard"
          >
            <option value="gentle">Gentle</option>
            <option value="standard">Standard</option>
            <option value="challenging">Challenging</option>
          </select>
        </div>
        <div>
          <label htmlFor="preferred_theme">Story theme (optional)</label>
          <select id="preferred_theme" name="preferred_theme" defaultValue="">
            <option value="">Pick from my interests</option>
            <option value="space">Space</option>
            <option value="football">Football</option>
            <option value="music">Music</option>
            <option value="explorer">Exploration</option>
          </select>
        </div>
        <div>
          <label htmlFor="learning_goal">Why are you learning Python?</label>
          <input id="learning_goal" name="learning_goal" maxLength={300} placeholder="optional" />
        </div>
        <div className="full">
          <button type="submit" disabled={busy}>
            {busy ? status : "Start my adventure"}
          </button>
        </div>
        {error && <div className="error-banner full">Something went wrong: {error}</div>}
      </form>
    </main>
  );
}
