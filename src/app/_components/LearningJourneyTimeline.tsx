'use client';

interface LearningStep {
  number: number;
  title: string;
  description: string;
  contentUrl: string;
}

interface LearningJourneyTimelineProps {
  steps: LearningStep[];
}

export default function LearningJourneyTimeline({ steps }: LearningJourneyTimelineProps) {
  return (
    <div className="relative w-full">
      {/* Vertical line connecting all steps */}
      <div className="absolute top-0 left-8 h-full w-0.5 bg-gray-300" />
      
      <div className="space-y-12">
        {steps.map((step, index) => (
          <div key={step.number} className="relative flex items-start">
            {/* Step number circle */}
            <div className="relative z-10 flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
              <span className="font-bold text-xl">{step.number}</span>
            </div>
            
            {/* Step content */}
            <div className="ml-8 flex-1 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="mb-2 font-semibold text-gray-900 text-xl">{step.title}</h3>
              <p className="mb-4 text-gray-600">{step.description}</p>
              <a
                href={step.contentUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                Access Content
                <svg
                  className="ml-2 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-label="External link"
                >
                  <title>External link</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 