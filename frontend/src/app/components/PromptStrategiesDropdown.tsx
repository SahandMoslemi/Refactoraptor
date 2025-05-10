"use client";

import React from "react";
import {
  StrategyInfo,
  PromptStrategyDropdownProps,
  STRAT_INFO_MAP,
  DEFAULT_STRATS
} from "../types/strategyTypes";
import { useDropdown } from "../utils/useDropdownUtils";

const PromptStratDropdown = ({
                         selectedPrompt,
                         setStrategy,
                         promptStrategies = DEFAULT_STRATS
                       }: PromptStrategyDropdownProps) => {
  // Use dropdown utility hook
  const { isOpen, toggleDropdown, dropdownRef, setIsOpen } = useDropdown();

  // Convert models array to ModelInfo array with descriptions when available
  const stratInfoList = promptStrategies.map(strat => {
    if (STRAT_INFO_MAP[strat]) {
      return STRAT_INFO_MAP[strat];
    } else {
      return {
        id: strat,
        name: strat,
        description: "Strategy"
      };
    }
  });

  // Find the name of the selected strategy
  const getSelectedStrategy = () => {
    if (!selectedPrompt) return "Select strategy";
    const stratInfo = stratInfoList.find(s => s.id === selectedPrompt);
    return stratInfo ? stratInfo.name : selectedPrompt;
  };

  // Handle strategy selection
  const handleSelectStrategy = (strategy: StrategyInfo) => {
    setStrategy(strategy.id);
    setIsOpen(false);
  };

  return (
      <div className="relative" ref={dropdownRef}>
        <button
            onClick={toggleDropdown}
            className="w-full bg-[#4c5944] rounded px-3 py-2 text-white text-left flex justify-between items-center focus:outline-none focus:ring-1 focus:ring-[#8ea382]"
        >
          <span>{getSelectedStrategy()}</span>
          <svg
              className={`w-4 h-4 transition-transform ${
                  isOpen ? "rotate-180" : ""
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
          >
            <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        {isOpen && (
            <div className="absolute z-10 w-full mt-1 bg-[#4c5944] rounded shadow-lg">
              {stratInfoList.map((strat) => (
                  <div
                      key={strat.id}
                      className="px-3 py-2 hover:bg-[#3d4937] cursor-pointer border-b border-[#5a6a50] last:border-b-0"
                      onClick={() => handleSelectStrategy(strat)}
                  >
                    <div className="font-medium">{strat.name}</div>
                    <div className="text-xs text-gray-300/70">
                      {strat.description}
                    </div>
                  </div>
              ))}
            </div>
        )}
      </div>
  );
};

export default PromptStratDropdown;