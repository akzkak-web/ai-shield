import type { SiteContent } from "./content";

export const zh: SiteContent = {
  seo: {
    title: "AI Shield - 让 AI 基础设施更安全",
    description:
      "AI Shield 帮助企业评估自托管 AI 推理环境的安全状态，识别配置风险，并提供清晰、可执行的整改建议。",
    ogTitle: "AI Shield - 让 AI 基础设施更安全",
    ogDescription:
      "面向自托管 AI 推理环境的证据化安全评估。看清暴露风险，识别配置问题，让每一项改进都有据可依。",
  },
  nav: {
    links: [
      { label: "平台", href: "#platform" },
      { label: "解决方案", href: "#solutions" },
      { label: "安全评估", href: "#how-it-works" },
      { label: "资源", href: "#report" },
      { label: "价格", href: "#pricing" },
    ],
    contactSales: "联系销售",
    requestDemo: "预约演示",
    menuAria: "打开导航菜单",
    languageAria: "切换语言",
  },
  hero: {
    badge: "AI 基础设施安全",
    headline1: "让 AI 基础设施更安全",
    headline2: "看清暴露风险，识别配置问题",
    description:
      "AI Shield 帮助企业评估自托管 AI 推理环境的安全状态，识别配置风险，并提供清晰、可执行的整改建议。",
    primaryCta: "申请安全评估",
    secondaryCta: "了解平台",
    props: [
      "基于证据的安全评估",
      "可执行的整改建议",
      "清晰的覆盖与风险视图",
    ],
    console: {
      title: "评估控制台",
      demo: "演示数据",
      topology: "环境拓扑",
      scope: "范围：仅限已授权目标",
      target: "目标：已授权",
      checks: "检查项",
      supported: "支持 6 项",
      checkNames: [
        "网络暴露",
        "身份认证",
        "CORS 策略",
        "模型 API 访问",
        "速率限制",
        "漏洞版本匹配",
      ],
      pass: "通过",
      unknown: "未确认",
      coverage: "覆盖度",
      coverageValue: "部分",
      footer: [
        "覆盖度：部分",
        "确认发现：0 项",
        "未确认项会如实报告，绝不视为安全",
      ],
    },
  },
  trust: {
    kicker: "为什么选择 AI SHIELD",
    title: "看清 AI 基础设施的安全状况",
    items: [
      {
        title: "识别暴露风险",
        body: "发现网络暴露与高风险的服务配置。",
      },
      {
        title: "验证安全控制",
        body: "评估身份认证、CORS、访问控制以及其他受支持的安全检查项。",
      },
      {
        title: "确定整改优先级",
        body: "把检查发现转化为切实可行、有证据支撑的整改建议。",
      },
    ],
  },
  platform: {
    kicker: "平台",
    title: "全面了解 AI 安全态势",
    sub: "从三个维度审视你运行的环境：哪些服务对外可达、哪些配置存在风险、哪些版本存在已知漏洞。",
    cards: [
      {
        title: "基础设施暴露面",
        body: "判断 AI 推理服务是否暴露在预期网络边界之外。",
      },
      {
        title: "安全配置审查",
        body: "审查受支持的身份认证、CORS、访问控制与服务配置信号。",
      },
      {
        title: "漏洞情报匹配",
        body: "将受支持的服务与版本信息，与可用的漏洞情报进行比对。",
      },
    ],
    visual: {
      auth: "身份认证",
      cors: "CORS 策略",
      modelAccess: "模型 API 访问",
      pass: "通过",
      unknown: "未确认",
      noAdvisories: "无匹配的受影响漏洞",
      nodes: ["暴露", "认证", "CORS", "CVE"],
    },
  },
  process: {
    kicker: "评估流程",
    title: "三步完成评估与整改",
    steps: [
      {
        title: "确认评估范围",
        body: "明确 AI 环境与已授权的评估目标。",
      },
      {
        title: "执行安全评估",
        body: "评估受支持的安全控制项，并收集技术证据。",
      },
      {
        title: "复核并整改",
        body: "获得包含发现、覆盖信息与整改建议的结构化报告。",
      },
    ],
  },
  capabilities: {
    kicker: "能力范围",
    title: "面向真实 AI 部署而设计",
    statusVerified: "已验证",
    statusSupported: "已支持",
    items: [
      { title: "网络暴露评估", body: "判断服务是否监听了预期边界之外的地址。" },
      { title: "身份认证配置审查", body: "检查模型端点是否要求身份凭证。" },
      { title: "CORS 配置审查", body: "识别过于宽松或反射任意来源的跨域策略。" },
      { title: "模型 API 访问审查", body: "检查未认证用户能否枚举模型列表。" },
      { title: "速率限制评估", body: "观察服务端点上的限流信号。" },
      { title: "漏洞版本匹配", body: "将检测到的服务版本与已知漏洞进行比对。" },
      { title: "基于证据的发现", body: "每一条发现都附带支撑它的证据。" },
      { title: "JSON 与 PDF 报告", body: "既提供结构化数据，也提供可阅读的评估报告。" },
      { title: "与基线对比", body: "将新的评估结果与已保存的基线进行差异比较。" },
    ],
    footnote:
      "Ollama 是当前版本唯一完成真实环境集成验证的评估目标。我们也具备其他推理服务的识别能力，但尚未完成真实环境验证。标记为「已验证」的检查项已完成真实服务集成测试；标记为「已支持」的能力已包含在当前产品中。",
  },
  report: {
    kicker: "评估报告",
    title: "每一条发现都能落地整改",
    body: "每次评估都会交付一份结构化报告：风险摘要、发现严重级别、支撑证据、覆盖范围与局限性，以及整改建议。",
    bullets: [
      "评估概览与风险摘要",
      "包含严重级别与证据的安全发现",
      "覆盖范围、局限性说明与整改建议",
    ],
    cta: "查看示例评估报告",
    mock: {
      header: "AI SHIELD 评估报告",
      demo: "演示数据",
      engagement: "委托编号：AISHIELD-DEMO-001",
      target: "目标：",
      targetValue: "已授权",
      risk: "风险摘要",
      severities: ["严重", "高危", "中危", "低危"],
      findingTitle: "AUTH-001 · 缺少身份认证",
      evidence: "证据：accessible_endpoints=['/v1/models', '/api/tags']",
      remediation: "整改建议：启用 API Key 认证，或在反向代理层增加身份认证。",
      coverage: "覆盖度",
      coverageValue: "部分 · 3 项未确认",
      limitations: "局限性说明",
      limitationsBody:
        "本次为只读评估，未确认的检查项会如实报告，绝不视为安全。",
    },
  },
  solutions: {
    kicker: "解决方案",
    title: "覆盖多种 AI 部署场景",
    items: [
      { title: "AI 部署服务商", body: "在客户依赖之前，验证你交付环境的安全状态。" },
      { title: "企业 IT 团队", body: "以独立视角了解内部自托管 AI 服务的真实状况。" },
      { title: "AI 应用公司", body: "了解推理层的配置方式，明确优先修复项。" },
      { title: "私有 AI 基础设施运营方", body: "让受控环境持续符合你自己的安全要求。" },
    ],
  },
  pricing: {
    kicker: "价格",
    title: "清晰直接的安全评估定价",
    quick: {
      label: "AI SHIELD 快速检查",
      price: "¥99",
      unit: "/ 次",
      body: "面向单个已授权 Ollama 环境的聚焦式安全基线评估。",
      features: [
        "六项受支持的安全检查",
        "技术证据复核",
        "安全发现摘要",
        "中文 PDF 报告",
        "整改建议",
        "约定范围内一次复测",
      ],
      cta: "申请评估",
    },
    enterprise: {
      label: "企业版 / 定制",
      title: "定制评估",
      body: "适用于多环境、长期合作，或经书面确认的扩展范围。",
      features: [
        "多个已授权目标",
        "按需选择检查项",
        "扩展报告与复测",
      ],
      cta: "联系销售",
    },
    note:
      "每次评估前都会以书面方式确认范围与排除项。AI Shield 提供的是聚焦式安全基线评估，不等同于全面渗透测试，也不包含订阅制服务或自动计费功能。",
  },
  faq: {
    kicker: "常见问题",
    title: "常见问题",
    items: [
      {
        q: "AI Shield 是什么？",
        a: "AI Shield 是面向自托管 AI 推理环境的安全评估平台。它通过只读检查审视已授权目标，并报告带有证据、严重级别、覆盖范围与整改建议的确认发现。",
      },
      {
        q: "目前支持哪些 AI 环境？",
        a: "Ollama 是当前版本唯一完成真实环境验证的评估目标。我们也具备其他推理服务的识别能力，但这些服务尚未完成真实环境验证。",
      },
      {
        q: "一次评估包含什么？",
        a: "六项受支持的检查：网络暴露、身份认证配置、CORS 配置、模型 API 访问、速率限制信号以及漏洞版本匹配。结果以结构化 JSON 与可阅读的 PDF 报告交付。",
      },
      {
        q: "需要提供模型访问权限吗？",
        a: "不需要。评估仅使用只读的服务端点，例如版本端点与模型列表端点，不会要求模型权重或模型数据。",
      },
      {
        q: "AI Shield 会向我的模型发送提示词吗？",
        a: "不会。标准评估只执行只读请求，不会向你的模型发送生成类提示词。",
      },
      {
        q: "评估范围如何获得授权？",
        a: "每次评估都始于书面授权与范围确认，其中列明准确的目标、端口与允许的动作。授权范围之外的主机绝不会被触碰。",
      },
      {
        q: "评估结束后会收到什么？",
        a: "一份结构化 JSON 结果，以及一份 PDF 报告，涵盖评估概览、带证据与严重级别的发现、整改建议、覆盖范围与局限性。",
      },
      {
        q: "报告没有发现问题，是否代表系统一定安全？",
        a: "不是。没有发现问题，只代表已执行的检查项中没有确认发现。报告会明确标注覆盖范围，未验证的检查项绝不会被当作安全。",
      },
    ],
  },
  finalCta: {
    title: "让 AI 基础设施更安全",
    body: "通过基于证据的安全评估，更清晰地了解你的 AI 部署安全态势。",
    primary: "申请安全评估",
    secondary: "联系团队",
  },
  footer: {
    tagline: "面向自托管 AI 推理环境的证据化安全评估。",
    product: "产品",
    solutions: "解决方案",
    resources: "资源",
    contact: "联系",
    platform: "平台",
    assessment: "安全评估",
    pricing: "价格",
    sampleReport: "示例报告",
    faq: "常见问题",
    privacy: "隐私政策",
    terms: "服务条款",
    contactNote: "评估仅针对已授权目标执行。",
    copyright: "© 2026 AI Shield. 保留所有权利。",
    whatsapp: "WhatsApp",
    telegram: "Telegram",
    chatNote: "想直接沟通？可以通过 WhatsApp 或 Telegram 联系我们。",
    whatsappMessage: "你好，我想咨询 AI Shield 安全评估。",
  },
  legal: {
    title: "法律信息",
    privacyTitle: "隐私政策",
    privacyBody:
      "初稿。AI Shield 仅将邮件咨询中提供的联系信息用于回复评估请求。评估只在已授权目标上执行，不收集客户的模型数据或模型内容。",
    termsTitle: "服务条款",
    termsBody:
      "初稿。每次评估都需要书面授权与已确认的范围。评估结果仅反映测试时的观察，不构成长期安全保证。上线前应由法律顾问完成这些文件的最终审定。",
  },
  subjects: {
    assessment: "安全评估申请",
    demo: "预约产品演示",
    sales: "联系 AI Shield 销售",
    custom: "定制评估咨询",
    team: "联系 AI Shield 团队",
  },
};
