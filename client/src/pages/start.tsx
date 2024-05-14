import { SignedOut, SignInButton } from "@clerk/clerk-react";

interface StartProps {}

export function Start(props: StartProps) {
  return (
    <>
      <main className="flex flex-col justify-center items-center h-full px-10">
        <div className="text-center">
          <h3 className="text-green-800 font-bold">Welcome to HealthAI</h3>
          <p className="text-sm italic text-green-800/70">
            Experience the new health care system,<br></br>that actually works!
          </p>
        </div>

        <SignedOut>
          <SignInButton>
            <button className="w-full bg-green-700 text-white py-2 border border-green-500 rounded-md my-5">
              Sign In
            </button>
          </SignInButton>
        </SignedOut>
      </main>
    </>
  );
}
