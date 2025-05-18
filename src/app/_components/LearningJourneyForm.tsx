"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LearningJourneyForm() {
  const [startPoint, setStartPoint] = useState("");
  const [endPoint, setEndPoint] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Encode the parameters to handle special characters in the URL
    const params = new URLSearchParams({
      start: startPoint,
      end: endPoint,
    });
    router.push(`/results?${params.toString()}`);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex w-full max-w-4xl flex-col gap-6 p-4"
    >
      <h1 className="text-center font-bold text-3xl">Learning Journey</h1>

      <div className="text-center text-gray-600">
        Thanks to Mantis, this app helps you create a personalized learning
        journey of content that will get you from your current level to your
        desired level.
        <br />
        For this we use our existing data base of content sources that we
        provide a recommended path through.
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="flex flex-col justify-between gap-2">
          <label
            htmlFor="endPoint"
            className="mb-2 block font-medium text-gray-700 text-sm"
          >
            What do you want to learn?
          </label>
          <p className="mb-2 text-gray-500 text-xs">
            Describe your learning goal. What do you want to learn and why? 
          </p>
          <textarea
            id="endPoint"
            value={endPoint}
            onChange={(e) => setEndPoint(e.target.value)}
            className="h-48 w-full rounded-md border border-gray-300 p-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
            placeholder="Describe your learning goal..."
            required
          />
        </div>

        <div className="flex flex-col justify-between gap-2">
          <label
            htmlFor="startPoint"
            className="mb-1 block font-medium text-gray-700 text-sm"
          >
            What's your current level?
          </label>
          <p className="mb-2 text-gray-500 text-xs">
            Tell us about your background, education and knowledge to help
            design your personalized learning journey. Include relevant fields
            and concepts you're familiar with.
          </p>
          <textarea
            id="startPoint"
            value={startPoint}
            onChange={(e) => setStartPoint(e.target.value)}
            className="h-48 w-full rounded-md border border-gray-300 p-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
            placeholder="Describe your background, context, and what you already know..."
            required
          />
        </div>
      </div>

      <button
        type="submit"
        className="mt-4 rounded-md bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Design My Journey
      </button>
    </form>
  );
}
