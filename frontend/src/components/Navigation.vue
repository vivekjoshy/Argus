<template>
    <div class="nav_row">
        <div class="navbar">
            <n-space justify="end">
                <div class="nav_items">
                    <n-button
                        type="primary"
                        icon-placement="left"
                        @click="authentication"
                    >
                        <template #icon>
                            <div v-if="isLoggedIn">
                                <n-icon>
                                    <login />
                                </n-icon>
                            </div>
                            <div v-else>
                                <n-icon>
                                    <logout />
                                </n-icon>
                            </div>
                        </template>
                        {{ loginText() }}
                    </n-button>
                </div>
            </n-space>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, inject } from "vue";
import { NButton, NIcon, NSpace } from "naive-ui";
import { Login, Logout } from "@vicons/tabler";

export default defineComponent({
    name: "GlobalNavigation",
    components: { NButton, NSpace, Login, Logout, NIcon },
    props: ["isLoggedIn"],
    setup(props) {
        const axios: any = inject("axios");
        function loginText(): string {
            if (props.isLoggedIn) {
                return "Logout";
            } else {
                return "Login";
            }
        }

        function authentication(): void {
            if (props.isLoggedIn) {
                axios
                    .get(`${window.location.origin}/api/v1.0/auth/logout`)
                    .then((response: any) => {
                        window.location.href = `${window.location.origin}`;
                    })
                    .catch((error: any) => {
                        window.location.href = `${window.location.origin}`;
                    });
            } else {
                window.location.href = `${window.location.origin}/api/v1.0/auth/login`;
            }
        }
        return { loginText, authentication };
    },
});
</script>

<style lang="scss" scoped>
.nav_items {
    padding: 1em;
}
</style>
