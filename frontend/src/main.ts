import { createApp } from "vue"

import App from "./App.vue"
import { useI18n } from "./composables/useI18n"
import "./style.css"

const { locale } = useI18n()
document.documentElement.setAttribute("lang", locale.value)

createApp(App).mount("#app")
