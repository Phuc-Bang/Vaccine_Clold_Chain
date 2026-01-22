import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatTemp(temp: number) {
  return `${temp.toFixed(1)}°C`;
}

export function getStatusColor(temp: number) {
  if (temp < 2 || temp > 8) return "text-red-500";
  if (temp > 6) return "text-yellow-500";
  return "text-green-500";
}
