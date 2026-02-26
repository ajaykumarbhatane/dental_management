import { create } from 'zustand';

const useUIStore = create((set) => ({
  sidebarOpen: true,
  mobileMenuOpen: false,
  searchQuery: '',

  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  setMobileMenuOpen: (open) => set({ mobileMenuOpen: open }),
  toggleMobileMenu: () => set((state) => ({ mobileMenuOpen: !state.mobileMenuOpen })),

  setSearchQuery: (query) => set({ searchQuery: query }),
}));

export default useUIStore;
