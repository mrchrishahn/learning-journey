import { HydrateClient } from "~/trpc/server";
import LearningJourneyTimeline from "~/app/_components/LearningJourneyTimeline";

// Sample data - in a real app, this would come from an API or database
const sampleSteps = [
  {
    number: 1,
    title: "Introduction to Core Concepts",
    description: "Start with the fundamental principles and basic terminology to build a strong foundation.",
    contentUrl: "https://example.com/step1"
  },
  {
    number: 2,
    title: "Practical Applications",
    description: "Learn how to apply the core concepts in real-world scenarios through hands-on examples.",
    contentUrl: "https://example.com/step2"
  },
  {
    number: 3,
    title: "Advanced Techniques",
    description: "Dive deeper into complex topics and explore advanced methodologies.",
    contentUrl: "https://example.com/step3"
  },
  {
    number: 4,
    title: "Mastery and Integration",
    description: "Combine all learned concepts and apply them to solve complex problems.",
    contentUrl: "https://example.com/step4"
  }
];

export default function ResultsPage({
  searchParams,
}: {
  searchParams: { start?: string; end?: string };
}) {
  const startPoint = searchParams.start || '';
  const endPoint = searchParams.end || '';

  return (
    <HydrateClient>
      <main className="flex min-h-screen flex-col items-center justify-center p-4">
        <div className="w-full max-w-4xl space-y-8">
          <h1 className="text-center font-bold text-3xl">Your Learning Journey</h1>
          
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-lg bg-gray-50 p-4">
              <h2 className="mb-2 font-semibold text-lg">Current Level</h2>
              <p className="whitespace-pre-wrap text-gray-700">{startPoint}</p>
            </div>
            
            <div className="rounded-lg bg-gray-50 p-4">
              <h2 className="mb-2 font-semibold text-lg">Learning Goal</h2>
              <p className="whitespace-pre-wrap text-gray-700">{endPoint}</p>
            </div>
          </div>

          <div className="mt-12">
            <h2 className="mb-8 text-center font-semibold text-2xl">Your Learning Path</h2>
            <LearningJourneyTimeline steps={sampleSteps} />
          </div>
        </div>
      </main>
    </HydrateClient>
  );
} 