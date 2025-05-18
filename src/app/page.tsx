import { HydrateClient } from "~/trpc/server";
import LearningJourneyForm from "~/app/_components/LearningJourneyForm";

export default async function Home() {
  return (
    <HydrateClient>
      <main className="flex min-h-screen flex-col items-center justify-center">
        <LearningJourneyForm />
      </main>
    </HydrateClient>
  );
}
