<template>
    <div class="home">
        <Navigation :is-logged-in="loggedIn" />
        <Footer />
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import Navigation from "@/components/Navigation.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
    name: "GlobalHome",
    components: {
        Navigation,
        Footer,
    },
    setup() {
        let loggedIn = ref(true);
        return { loggedIn };
    },
});
</script>

<style lang="scss"></style>
