import { UserButton, useUser } from "@clerk/clerk-react";
import { FormEvent, useState } from "react";
import { BASE_URL } from "../consts";
import { useNavigate } from "react-router-dom";

interface OnboardingProps {
  refetch(user: any): Promise<void>;
}

export function Onboarding(props: OnboardingProps) {
  const [form, setForm] = useState<{ age: string; gender: string }>({
    age: "0",
    gender: "male",
  });

  const { user } = useUser();

  const navigate = useNavigate();

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!user) return;
    console.log(form);

    const res = await fetch(`${BASE_URL}/onboard-user`, {
      method: "POST",
      body: JSON.stringify({ ...form, user_id: user.id }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await res.json();
    if (data && data.status) {
      props.refetch(user);
    }
  }

  if (!user) {
    return <></>;
  }

  return (
    <main className="flex flex-col justify-start items-start h-full">
      <div className="py-4 border-b w-full px-5 flex items-center justify-between">
        <h3>OnBoarding</h3>
        <UserButton />
      </div>

      <div className="px-5 py-5">
        <h2 className="text-lg font-bold text-green-800 mb-5">
          Finish On-Boarding to start using HealthAI!
        </h2>
        <form onSubmit={onSubmit}>
          <div className="mb-5">
            <label className="block mb-1" htmlFor="age">
              Age
            </label>
            <input
              className="w-full border border-green-800 p-2 rounded-md outline-green-700"
              type="number"
              id="age"
              placeholder="Age"
              onChange={(e) => setForm((f) => ({ ...f, age: e.target.value }))}
              value={form.age}
            />
          </div>
          <div>
            <label className="block mb-1" htmlFor="gender">
              Gender
            </label>
            <select
              className="w-full border border-green-800 p-2 rounded-md outline-green-700"
              id="gender"
              onChange={(e) =>
                setForm((f) => ({ ...f, gender: e.target.value }))
              }
              value={form.gender}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div className="w-full absolute bottom-5 left-0 px-5 pt-5 border-t flex items-center justify-center">
            <button className="w-full bg-green-700 text-white p-2 rounded-md">
              Save and Continue
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
