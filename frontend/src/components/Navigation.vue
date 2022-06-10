<template>
    <div class="nav_row">
        <div class="navbar">
            <n-space justify="end">
                <div class="nav_items">
                    <n-button
                        type="primary"
                        icon-placement="left"
                        @click="$router.push('login')"
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
import { defineComponent } from "vue";
import { NButton, NIcon, NSpace } from "naive-ui";
import { Login, Logout } from "@vicons/tabler";
export default defineComponent({
    name: "GlobalNavigation",
    components: { NButton, NSpace, Login, Logout, NIcon },
    props: ["isLoggedIn"],
    setup(props) {
        function loginText(): string {
            if (props.isLoggedIn) {
                return "Login";
            } else {
                return "Logout";
            }
        }
        return { loginText };
    },
});
</script>

<style lang="scss" scoped>
.nav_items {
    padding: 1em;
}
</style>
