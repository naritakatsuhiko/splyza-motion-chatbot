import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const { message } = await req.json();
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) throw new Error("API Key is missing");

    // 1. Motionナレッジの読み込み
    const knowledgeDir = path.join(process.cwd(), "src/data/knowledge");
    const files = fs.readdirSync(knowledgeDir);
    let systemPrompt = "";
    let knowledgeBase = "";

    files.forEach((file) => {
      if (file.endsWith(".md")) {
        const content = fs.readFileSync(path.join(knowledgeDir, file), "utf-8");
        if (file.includes("System_Prompt")) systemPrompt = content;
        else knowledgeBase += `\n--- FILE: ${file} ---\n${content}\n`;
      }
    });

    // 2. APIエンドポイントの設定
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=${apiKey}`;

    const payload = {
      system_instruction: { parts: [{ text: systemPrompt }] },
      contents: [{ role: "user", parts: [{ text: `以下のナレッジベースのみを根拠として回答してください。\n\n【ナレッジベース】\n${knowledgeBase}\n\n【ユーザーの質問】\n${message}` }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: 4096 }
    };

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) throw new Error(JSON.stringify(data));

    const text = data.candidates[0].content.parts[0].text;
    return NextResponse.json({ text });

  } catch (error: any) {
    console.error("❌ Motion API Error:", error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
