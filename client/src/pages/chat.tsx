import { UserButton, useUser } from "@clerk/clerk-react";
import { BASE_URL } from "../consts";
import { useEffect, useRef, useState } from "react";
import { Bars3Icon, PaperAirplaneIcon } from "@heroicons/react/24/solid";
import { useNavigate, useSearchParams } from "react-router-dom";

interface ChatProps {}

export function Chat(props: ChatProps) {
  const [urlSearchParams] = useSearchParams();
  const chatId = urlSearchParams.get("chatId");
  const convoId = chatId;

  const navigate = useNavigate();

  const ref = useRef<HTMLDivElement>(null);

  const [convos, setConvos] = useState<Array<any>>([]);
  const [menuIsOpen, setMenuIsOpen] = useState<boolean>(false);

  const { isLoaded, user } = useUser();

  const [input, setInput] = useState<string>("");
  const [loadingResponse, setLoadingResponse] = useState<boolean>(false);

  async function getConvo() {
    const convo = await fetch(`${BASE_URL}/get-convo/${convoId}`);
    const data = await convo.json();
    setConvos(data.convo);
  }

  function stringifyConvos(convos: Array<any>) {
    let chat = "";

    for (let i = 0; i < convos.length; i++) {
      chat += convos[i].role === "user" ? "User: " : "Assistant: ";
      chat += convos[i].content + "\n";
    }

    return chat;
  }

  async function sendChat() {
    if (!user || !input) return;
    setLoadingResponse(true);
    setConvos([...convos, { role: "user", content: input }]);
    ref.current?.scrollTo({
      top: ref.current.getBoundingClientRect().bottom,
      behavior: "smooth",
    });

    const res = await fetch(`${BASE_URL}/convo-chat`, {
      method: "POST",
      body: JSON.stringify({
        convo_id: convoId,
        content: input,
        history: stringifyConvos(convos),
        user_id: user.id,
        len: convos.length,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await res.json();

    console.log(data);

    if (data.status !== "success") return;

    setConvos([
      ...convos,
      { role: "user", content: input },
      { role: "assistant", content: data.response },
    ]);

    setInput("");

    setLoadingResponse(false);

    ref.current?.scrollTo({
      top: ref.current.getBoundingClientRect().bottom,
      behavior: "smooth",
    });
  }

  useEffect(() => {
    getConvo();
  }, []);

  if (!isLoaded || !user) {
    return <div>Loading...</div>;
  }

  return (
    <main className="flex flex-col justify-start items-start h-full">
      <div className="py-4 border-b w-full px-5 flex items-center justify-between">
        <h3>Chat</h3>
        <UserButton />
      </div>

      <div className="w-full h-full overflow-y-scroll mb-20" ref={ref}>
        {convos.map((c) => (
          <>
            {c.role === "user" ? (
              <div className="w-full flex flex-col items-start justify-start px-5 py-5 border-b">
                <div className="w-full flex items-start justify-start gap-2">
                  <div className="h-10 aspect-square bg-green-800 rounded-full">
                    <img
                      className="h-10 aspect-square rounded-full"
                      src={user.imageUrl}
                      alt=""
                    />
                  </div>
                  <div className="w-full flex flex-col items-start justify-start">
                    <div className="text-black rounded-md px-3 py-2">
                      {c.content}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="w-full flex flex-col items-start justify-start px-5 py-5 border-b">
                <div className="w-full flex items-start justify-start gap-2">
                  <div className="h-10 aspect-square bg-green-800 rounded-full">
                    <img
                      src="/doc.jpg"
                      className="h-10 aspect-square rounded-full"
                      alt=""
                    />
                  </div>
                  <div className="w-full flex flex-col items-start justify-start">
                    <div className="text-black rounded-md px-3 py-2">
                      {c.content.startsWith("Assistant:")
                        ? c.content.replace("Assistant:", "")
                        : c.content.replace('"', "").replace('"', "")}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        ))}
        {loadingResponse && (
          <div className="w-full flex flex-col items-start justify-start px-5 py-5 border-b">
            <div className="w-full flex items-start justify-start gap-2">
              <div className="h-10 aspect-square bg-green-800 rounded-full">
                <img
                  src="/doc.jpg"
                  className="h-10 aspect-square rounded-full"
                  alt=""
                />
              </div>
              <div className="w-full flex flex-col items-start justify-start">
                <div className="text-black rounded-md px-3 py-2">
                  <img src="/generating.gif" className="w-8" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="w-full px-5 py-5 absolute bg-white bottom-0 border-t">
        <div className="relative flex items-center justify-center gap-2">
          {menuIsOpen && (
            <div className="menu popup-anim absolute bottom-full border border-zinc-300 mb-2 rounded-md p-2 bg-zinc-50 w-full z-10">
              <p className="font-bold text-zinc-700 mb-3">More Options</p>
              <ul>
                <li className="border-b p-2">
                  <button
                    onClick={() => navigate(`/summary?chatId=${convoId}`)}
                  >
                    Medical Summary
                  </button>
                </li>
                <li className="p-2">
                  <button
                    onClick={() => navigate(`/care-plan?chatId=${convoId}`)}
                  >
                    Care Plan
                  </button>
                </li>
              </ul>
            </div>
          )}
          <textarea
            disabled={loadingResponse}
            className="w-full border rounded-md px-3 py-2 outline-green-800"
            placeholder="Enter query..."
            value={input}
            name="input"
            onChange={(e) => setInput(e.target.value)}
            rows={1}
          />
          <button
            disabled={loadingResponse}
            onClick={sendChat}
            className="bg-green-800 flex justify-center items-center w-14 aspect-square text-white rounded-md"
          >
            <PaperAirplaneIcon width={20} />
          </button>
          <button
            disabled={loadingResponse}
            onClick={() => setMenuIsOpen((b) => !b)}
            className="bg-green-800 flex justify-center items-center w-14 aspect-square text-white rounded-md"
          >
            <Bars3Icon width={20} />
          </button>
        </div>
      </div>
    </main>
  );
}
