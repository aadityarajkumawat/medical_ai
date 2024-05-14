import { UserButton } from "@clerk/clerk-react";
import { useSearchParams } from "react-router-dom";
import { BASE_URL } from "../consts";
import { useEffect, useState } from "react";
import { ArrowPathIcon } from "@heroicons/react/24/solid";
import { marked } from "marked";

export function Summary() {
  const [log, setLog] = useState("");
  const [convo, setConvo] = useState<any>();

  const [summary, setSummary] = useState<any>();
  const [html, setHtml] = useState("");

  const [urlSearchParams] = useSearchParams();
  const chatId = urlSearchParams.get("chatId");
  const convoId = chatId;

  async function medicalConvo() {
    const convo = await fetch(`${BASE_URL}/get-medical-convo/${convoId}`);
    const data = await convo.json();
    const medicalConvo = data.medical_convo;
    setConvo(medicalConvo);
    setLog((d) => d + JSON.stringify(data, null, 4));
  }

  async function getSummary() {
    const convo = await fetch(`${BASE_URL}/get-summary/${convoId}`);
    const data = await convo.json();
    setSummary(data.summary);
    setLog((d) => d + JSON.stringify(data, null, 4));
  }

  async function loadHtml() {
    setHtml(
      await marked(
        summary.summary.replace("Corrected Summary", "").replace("[STOP]", "")
      )
    );
  }

  useEffect(() => {
    // combine();
    medicalConvo();
    getSummary();
  }, []);

  useEffect(() => {
    if (!summary) return;
    loadHtml();
  }, [summary]);

  if (!convo || !summary) {
    return (
      <>
        <main className="flex flex-col justify-start items-start h-full">
          <div className="py-4 border-b w-full px-5 flex items-center justify-between">
            <h3>Chat Summary </h3>
            <UserButton />
          </div>
          <div className="px-5 py-4 flex flex-col items-center justify-center w-full">
            <h3 className="mb-5">HealthAI Summary Generation</h3>
            <img className="w-10" src="/spinner.gif" alt="" />
            <p className="text-center">
              Please wait, summary generation usually takes 3-4 minutes
            </p>
          </div>
        </main>
        {/* <p>f: {log}</p> */}
      </>
    );
  }

  return (
    <main className="flex flex-col justify-start items-start h-full">
      <div className="py-4 border-b w-full px-5 flex items-center justify-between">
        <h3>Chat Summary </h3>
        <UserButton />
      </div>

      <div className="px-5">
        <h2 className="mt-3 font-bold text-zinc-700">
          {convo.convo_name.replace('"', "").replace('"', "")}
        </h2>
        <div className="flex items-center justify-start gap-2">
          <p className="text-sm italic text-zinc-600">
            Last updated: {new Date(summary.created_at).toDateString()}
          </p>
        </div>
        <div
          className="mt-3 marked"
          dangerouslySetInnerHTML={{ __html: html }}
        ></div>
      </div>

      {/* {log} */}
    </main>
  );
}
