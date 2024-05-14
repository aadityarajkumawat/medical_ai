import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import * as serviceWorkerRegistration from "./serviceWorkerRegistration";
import reportWebVitals from "./reportWebVitals";
import { ClerkProvider } from "@clerk/clerk-react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Chat } from "./pages/chat";
import { Summary } from "./pages/summary";
import { CarePlan } from "./pages/care-plan";
import { Onboarding } from "./pages/onboarding";

const clerkPubKey = process.env.REACT_APP_PUB_KEY;

console.log(process.env);

if (!clerkPubKey) {
  throw new Error("REACT_APP_PUB_KEY is required");
}

const routes = createBrowserRouter([
  { path: "/", element: <App /> },
  { path: "/chat", element: <Chat /> },
  { path: "/summary", element: <Summary /> },
  { path: "/care-plan", element: <CarePlan /> },
]);

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <React.StrictMode>
    <ClerkProvider publishableKey={clerkPubKey}>
      <RouterProvider router={routes} />
      {/* <App /> */}
    </ClerkProvider>
  </React.StrictMode>
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://cra.link/PWA
serviceWorkerRegistration.unregister();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
