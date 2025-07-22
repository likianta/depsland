import { defineConfig } from 'vitepress'
import { withMermaid } from "vitepress-plugin-mermaid"

export default withMermaid({
    // your existing vitepress config...
    ...defineConfig({
      title: "Depsland",
      description: "Depsland WIKI site.",
      themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
          { text: 'Home', link: '/' },
          { text: 'Examples', link: '/markdown-examples' }
        ],

        search: {
          provider: 'local'
        },

        sidebar: [
          {
            text: 'Examples',
            items: [
              { text: 'Markdown Examples', link: '/markdown-examples' },
              { text: 'Runtime API Examples', link: '/api-examples' }
            ]
          },
          {
            text: '话题',
            items: [
              { text: '迷你启动器', link: '/topics/mini-launcher' }
            ]
          }
        ],

        socialLinks: [
          { icon: 'github', link: 'https://github.com/likianta/depsland' }
        ]
      }
    }),
    // optionally, you can pass MermaidConfig
    mermaid: {
      // refer https://mermaid.js.org/config/setup/modules/mermaidAPI.html#mermaidapi-configuration-defaults for options
    },
    // optionally set additional config for plugin itself with MermaidPluginConfig
    mermaidPlugin: {
      class: "mermaid my-class", // set additional css classes for parent container 
    },
});

// https://vitepress.dev/reference/site-config
// export default defineConfig({
//   title: "Depsland",
//   description: "Depsland WIKI site.",
//   themeConfig: {
//     // https://vitepress.dev/reference/default-theme-config
//     nav: [
//       { text: 'Home', link: '/' },
//       { text: 'Examples', link: '/markdown-examples' }
//     ],

//     search: {
//       provider: 'local'
//     },

//     sidebar: [
//       {
//         text: 'Examples',
//         items: [
//           { text: 'Markdown Examples', link: '/markdown-examples' },
//           { text: 'Runtime API Examples', link: '/api-examples' }
//         ]
//       },
//       {
//         text: '话题',
//         items: [
//           { text: '迷你启动器', link: '/topics/mini-launcher' }
//         ]
//       }
//     ],

//     socialLinks: [
//       { icon: 'github', link: 'https://github.com/likianta/depsland' }
//     ]
//   }
// })
