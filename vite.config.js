import { defineConfig } from "vite";
import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import cssnano from "cssnano";
import path from "path";

export default defineConfig(({ mode }) => {
  const isProduction = mode === "production";

  return {
    css: {
      postcss: {
        plugins: [
          tailwindcss(),
          autoprefixer(),
          isProduction && cssnano(),
        ].filter(Boolean),
      },
    },
    build: {
      outDir: "static",
      emptyOutDir: false,
      rollupOptions: {
        input: [
          path.resolve(__dirname, "static/assets/scss/custom.scss"),
          // Tailwind source lives under assets/tw to avoid overwriting built CSS
          path.resolve(__dirname, "static/assets/tw/public.css"),
        ],
        output: {
          assetFileNames: (assetInfo) => {
            if (assetInfo.name === "custom.css") {
              return "assets/css/custom.css";
            }
            if (assetInfo.name === "public.css") {
              return "assets/css/public.css";
            }
            return "assets/css/[name].[ext]";
          },
        },
      },
    },
  };
});