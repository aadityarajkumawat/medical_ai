import { UserButton, useUser } from "@clerk/clerk-react";
import { BASE_URL } from "../consts";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface HomeProps {}

export function Home(props: HomeProps) {
  const { user, isLoaded } = useUser();

  const [convos, setConvos] = useState<Array<any>>([]);
  const navigate = useNavigate();

  async function getConvos(user_id: string) {
    console.log("Getting conversations");
    const res = await fetch(`${BASE_URL}/medical-convo/${user_id}`);

    const data = await res.json();
    const medicalConvos = data.medical_convos;
    setConvos(medicalConvos);
  }

  async function createNewConvo(user_id: string) {
    console.log("Creating new conversation");
    const res = await fetch(`${BASE_URL}/medical-convo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ user_id }),
    });

    const { id } = await res.json();

    navigate(`/chat?chatId=${id}`);
  }

  useEffect(() => {
    async function fetchData() {
      if (!user) return;
      await getConvos(user.id);
    }

    fetchData();
  }, [user]);

  if (!isLoaded || !user) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <main className="flex flex-col justify-start items-start h-full">
        <div className="py-4 border-b w-full px-5 flex items-center justify-between">
          <h3>Past Chats</h3>
          <UserButton />
        </div>
        <div className="px-5 w-full mt-5">
          {convos.map((convo) => (
            <div
              key={convo.id}
              className="flex flex-col justify-between items-center py-2 border rounded-md w-full px-3 mb-5"
              onClick={() => {
                // props.setConvoId(convo.id);
                // props.pushTo("/chat");
                navigate(`/chat?chatId=${convo.id}`);
              }}
            >
              <div className="w-full">
                <p>{convo.convo_name.replace('"', "").replace('"', "")}</p>
                <p className="text-sm text-zinc-600">
                  {new Date(convo.updated_at).toDateString()}
                </p>
              </div>

              {/* <div className="w-full flex items-center justify-between gap-2">
                <button className="bg-green-700 w-1/2 text-white px-2 py-1 rounded-md">
                  Summary
                </button>
                <button className="bg-green-700 w-1/2 text-white px-2 py-1 rounded-md">
                  Care Plan
                </button>
              </div> */}
            </div>
          ))}
        </div>

        <div className="px-5 w-full absolute bottom-0">
          <button
            onClick={() => createNewConvo(user.id)}
            className="w-full bg-green-700 text-white py-2 border border-green-500 rounded-md my-5"
          >
            New Conversation
          </button>
        </div>
      </main>
    </>
  );
}
