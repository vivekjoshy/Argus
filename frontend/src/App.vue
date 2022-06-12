<template>
    <n-config-provider
        style="width: 100%; height: 100%"
        :theme="getTheme"
        :theme-overrides="themeOverrides"
    >
        <n-notification-provider>
            <router-view />
            <n-global-style />
        </n-notification-provider>
    </n-config-provider>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue";
import {
    darkTheme,
    NConfigProvider,
    NGlobalStyle,
    NNotificationProvider,
} from "naive-ui";
import { themeStore } from "@/stores/theme";
import dark from "@/settings/themes/dark";
import light from "@/settings/themes/light";

export default defineComponent({
    name: "GlobalApp",
    components: {
        NConfigProvider,
        NNotificationProvider,
        NGlobalStyle,
    },
    setup() {
        const store = themeStore();
        const themeOverrides = computed(() => (store.dark ? dark : light));
        const getTheme = computed(() => (store.dark ? darkTheme : undefined));
        return { themeOverrides, getTheme };
    },
});
</script>

<style lang="scss"></style>
