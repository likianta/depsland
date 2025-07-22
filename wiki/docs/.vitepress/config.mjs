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
            text: '话题',
            items: [
              { text: '迷你启动器', link: '/topics/mini-launcher' }
            ]
          },
          {
            text: '设计思考',
            items: [
              { 
                text: 'Dist 目录结构设计', 
                link: '/design-thinking/why-dist-tree-like-this' 
              },
              { 
                text: 'Manifest 路径格式转换', 
                link: '/design-thinking/manifest-path-format' 
              },
              { 
                text: 'PYPI 索引文件格式', 
                link: '/design-thinking/pypi-index-file-format' 
              },
            ]
          },
          {
            text: '开发备忘',
            items: [
              {
                text: 'Python 版本迁移注意事项',
                link: '/devnote/upgrade-python-standalone-version'
              },
              {
                text: '制作启动器图标',
                link: '/devnote/launcher-icon-setting'
              },
              {
                text: '自升级功能构想 (已过时)',
                link: '/devnote/outdated/self-upgrade-plan'
              },
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
