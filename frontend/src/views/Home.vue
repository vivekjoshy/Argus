<template>
    <div class="home">
        <Navigation :is-logged-in="loggedIn" />
        <Footer />
    </div>
</template>

<script lang="ts">
import { defineComponent, inject, onMounted, ref } from "vue";
import Navigation from "@/components/Navigation.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
    name: "GlobalHome",
    components: {
        Navigation,
        Footer,
    },
    setup() {
        const axios: any = inject("axios");
        let loggedIn = ref(false);
        onMounted(() => {
            axios
                .get(`${window.location.origin}/api/v1.0/auth/authorized`)
                .then((response: any) => {
                    loggedIn.value = response.status === 200;
                })
                .catch((error: any) => {
                    loggedIn.value = false;
                });
        });
        return { loggedIn };
    },
});
</script>

<style lang="scss">
.home {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
</style>
