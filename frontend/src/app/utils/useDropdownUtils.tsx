// app/utils/useDropdownUtils.tsx
// Utility hook for dropdown functionality

import { useState, useRef, useEffect } from 'react';

/**
 * Custom hook for managing dropdown state and outside click handling
 * @returns Object containing dropdown state and refs
 */
export function useDropdown() {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Handle clicking outside to close dropdown
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const toggleDropdown = () => setIsOpen(!isOpen);

    return {
        isOpen,
        setIsOpen,
        toggleDropdown,
        dropdownRef
    };
}