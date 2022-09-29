import createVanilla from "zustand/vanilla";
import create from "zustand";

type TTeamStore = {
  users: string[];
  currentUser: string;
  setCurrentUser: (currentUser: string) => void;
};

export const teamStore = createVanilla<TTeamStore>((set, get) => ({
  users: ["anna", "jaquelin", "eugene", "mark"],
  currentUser: "mark",
  setCurrentUser: (currentUser) => set({ currentUser }),
}));

export const useTeamStore = create(teamStore);
