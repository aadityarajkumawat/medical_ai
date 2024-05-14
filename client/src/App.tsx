import { useEffect, useState } from "react";
import { Start } from "./pages/start";
import { SignedIn, SignedOut, useUser } from "@clerk/clerk-react";
import { Home } from "./pages/home";
import { BASE_URL } from "./consts";
import { Onboarding } from "./pages/onboarding";

export default function App() {
  const { user, isSignedIn } = useUser();

  const [onBoarded, setOnBoarded] = useState<boolean>(false);
  const [loading, setLoading] = useState(false);

  async function fetchUser(user: any) {
    setLoading(true);
    const res = await fetch(`${BASE_URL}/user-profile/${user.id}`);
    const data = await res.json();

    console.log(data);

    if (!data.user) {
      setOnBoarded(!!data.user);
      setLoading(false);

      return;
    }

    setOnBoarded(data.user.age && data.user.gender);
    setLoading(false);
  }

  useEffect(() => {
    if (!user) return;
    fetchUser(user);
  }, [user]);

  console.log(user, isSignedIn, loading, !user && isSignedIn);

  if (!user && isSignedIn) {
    return <></>;
  }

  return (
    <>
      <SignedOut>
        <Start />
      </SignedOut>
      <SignedIn>
        {!loading && (
          <>{onBoarded ? <Home /> : <Onboarding refetch={fetchUser} />}</>
        )}
      </SignedIn>
    </>
  );
}
