<template>
    <div class="footer">
        <n-space justify="space-around" size="large">
            <n-space vertical>
                <div class="policy-header">
                    <p><b>Policies</b></p>
                </div>
                <div v-for="(link, key) in policyLinks">
                    <router-link :to="link[0]">
                        <n-button text="true" :key="key">
                            {{ link[1] }}
                        </n-button>
                    </router-link>
                </div>
            </n-space>
            <n-space vertical>
                <div class="resource-header">
                    <p><b>Resources</b></p>
                </div>
                <div v-for="(link, key) in resourceLinks">
                    <n-button text="true" :key="key">
                        <a :href="link[0]">
                            {{ link[1] }}
                        </a>
                    </n-button>
                </div>
            </n-space>
            <n-space vertical>
                <div class="theme-header">
                    <p><b>Theme</b></p>
                </div>
                <n-switch v-model:value="active" @update:value="updateTheme">
                    <template #checked> Dark </template>
                    <template #unchecked> Light </template>
                </n-switch>
            </n-space>
        </n-space>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { NSpace, NSwitch } from "naive-ui";
import { RouterLink } from "vue-router";
import { themeStore } from "@/stores/theme";

let active = ref(false);

const policyLinks = {
    terms: ["/terms", "Terms"],
    privacy: ["/privacy", "Privacy"],
};

const resourceLinks = {
    github: ["https://github.com/OpenDebates/Argus", "Github"],
    forum: ["https://forum.opendebates.net", "Forum"],
};

export default defineComponent({
    name: "GlobalFooter",
    components: {
        NSpace,
        NSwitch,
        RouterLink,
    },
    setup(props, context) {
        const theme = themeStore();

        function updateTheme(value: boolean) {
            theme.switchTheme();
        }
        return {
            active,
            policyLinks,
            resourceLinks,
            updateTheme,
        };
    },
});
</script>

<style lang="scss" scoped>
.footer {
    padding: 2em;
    background-color: #181818;
    margin-top: auto;
}

a {
    color: #e5dfdf;
    text-decoration: none;
}

p {
    color: rgba(255, 255, 255, 0.82);
}
</style>
