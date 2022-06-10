import { defineStore } from "pinia";
import type { GlobalThemeOverrides } from "naive-ui";
import dark from "@/settings/themes/dark";
import light from "@/settings/themes/light";

export const themeStore = defineStore("main", {
    state: () => {
        return {
            dark: true,
        };
    },
    getters: {
        getOverrides(state: Record<string, boolean>): GlobalThemeOverrides {
            if (state.dark) {
                return dark;
            } else {
                return light;
            }
        },
    },
});
