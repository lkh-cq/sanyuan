/* Sanyuan Context Router */
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/main.ts
var main_exports = {};
__export(main_exports, {
  default: () => SanyuanContextRouter
});
module.exports = __toCommonJS(main_exports);
var import_obsidian2 = require("obsidian");

// src/client.ts
var import_obsidian = require("obsidian");
function isLoopback(hostname) {
  return hostname === "127.0.0.1" || hostname === "localhost" || hostname === "[::1]";
}
function endpointUrl(settings, path) {
  const endpoint = new URL(settings.endpoint);
  if (endpoint.protocol !== "http:" && endpoint.protocol !== "https:") {
    throw new Error("The sidecar endpoint must use HTTP or HTTPS.");
  }
  if (!isLoopback(endpoint.hostname) && !settings.allowRemoteEndpoint) {
    throw new Error("Remote endpoints require explicit opt-in in settings.");
  }
  const base = endpoint.toString().replace(/\/$/, "");
  return `${base}${path}`;
}
function headers(settings) {
  const result = { "Content-Type": "application/json" };
  if (settings.authToken.trim()) {
    result.Authorization = `Bearer ${settings.authToken.trim()}`;
  }
  return result;
}
function requireObject(value) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("The sidecar returned an invalid JSON object.");
  }
  return value;
}
var SanyuanClient = class {
  constructor(settings) {
    this.settings = settings;
  }
  async health() {
    const response = await (0, import_obsidian.requestUrl)({
      url: endpointUrl(this.settings, "/health"),
      method: "GET",
      headers: headers(this.settings),
      throw: false
    });
    if (response.status < 200 || response.status >= 300) {
      throw new Error(`Sidecar health check failed with HTTP ${response.status}.`);
    }
    const data = requireObject(response.json);
    return {
      status: typeof data.status === "string" ? data.status : "unknown",
      embedding_enabled: typeof data.embedding_enabled === "boolean" ? data.embedding_enabled : void 0,
      routing_loaded: typeof data.routing_loaded === "boolean" ? data.routing_loaded : void 0
    };
  }
  async retrieve(request) {
    const response = await (0, import_obsidian.requestUrl)({
      url: endpointUrl(this.settings, "/v1/retrieve-and-inject"),
      method: "POST",
      headers: headers(this.settings),
      contentType: "application/json",
      body: JSON.stringify(request),
      throw: false
    });
    if (response.status < 200 || response.status >= 300) {
      const data2 = requireObject(response.json);
      const message = typeof data2.error === "string" ? data2.error : `HTTP ${response.status}`;
      throw new Error(`Retrieval failed: ${message}`);
    }
    const data = requireObject(response.json);
    if (typeof data.query !== "string" || typeof data.triggered !== "boolean" || typeof data.mode !== "string" || typeof data.injection !== "string") {
      throw new Error("The sidecar retrieval response is incomplete.");
    }
    return {
      query: data.query,
      triggered: data.triggered,
      mode: data.mode,
      injection: data.injection,
      diagnostics: typeof data.diagnostics === "object" && data.diagnostics !== null ? data.diagnostics : {}
    };
  }
};

// src/types.ts
var DEFAULT_SETTINGS = {
  endpoint: "http://127.0.0.1:8765",
  topK: 8,
  mode: "full",
  smartTriggerPolicy: "auto",
  authToken: "",
  allowRemoteEndpoint: false
};

// src/main.ts
function parseAxes(value) {
  if (Array.isArray(value)) {
    const axes = value.map(String).map((axis) => axis.trim()).filter(Boolean);
    return axes.length ? axes : void 0;
  }
  if (typeof value === "string") {
    const axes = value.split(",").map((axis) => axis.trim()).filter(Boolean);
    return axes.length ? axes : void 0;
  }
  return void 0;
}
var QueryModal = class extends import_obsidian2.Modal {
  constructor(plugin, submit) {
    super(plugin.app);
    this.submit = submit;
    this.query = "";
  }
  onOpen() {
    this.setTitle("Retrieve context");
    const input = new import_obsidian2.TextAreaComponent(this.contentEl).setPlaceholder("Enter a retrieval query").onChange((value) => {
      this.query = value;
    });
    input.inputEl.rows = 5;
    input.inputEl.addClass("sanyuan-context-query");
    const actions = this.contentEl.createDiv({ cls: "sanyuan-context-actions" });
    new import_obsidian2.ButtonComponent(actions).setButtonText("Retrieve").setCta().onClick(() => {
      const query = this.query.trim();
      if (!query) {
        new import_obsidian2.Notice("Enter a query first.");
        return;
      }
      this.close();
      void this.submit(query);
    });
  }
  onClose() {
    this.contentEl.empty();
  }
};
var ResultModal = class extends import_obsidian2.Modal {
  constructor(plugin, result, editor) {
    super(plugin.app);
    this.result = result;
    this.editor = editor;
  }
  onOpen() {
    this.setTitle(this.result.triggered ? "Retrieved context" : "Retrieval skipped");
    const output = this.contentEl.createEl("pre", {
      cls: "sanyuan-context-result",
      text: this.result.injection
    });
    output.setAttr("tabindex", "0");
    const actions = this.contentEl.createDiv({ cls: "sanyuan-context-actions" });
    new import_obsidian2.ButtonComponent(actions).setButtonText("Copy").onClick(() => {
      void navigator.clipboard.writeText(this.result.injection).then(() => {
        new import_obsidian2.Notice("Context copied.");
      }).catch(() => {
        new import_obsidian2.Notice("Clipboard access failed. Select the preview text instead.", 7e3);
      });
    });
    if (this.editor) {
      new import_obsidian2.ButtonComponent(actions).setButtonText("Insert as frontmatter").onClick(() => {
        this.writeContextFrontmatter();
        this.close();
      });
    }
    if (this.editor && this.result.triggered) {
      new import_obsidian2.ButtonComponent(actions).setButtonText("Insert").setCta().onClick(() => {
        var _a;
        (_a = this.editor) == null ? void 0 : _a.replaceSelection(`

${this.result.injection}
`);
        this.close();
      });
    }
  }
  onClose() {
    this.contentEl.empty();
  }
  writeContextFrontmatter() {
    const editor = this.editor;
    if (!editor) {
      return;
    }
    const context = [
      "sanyuan_context:",
      `  query: ${this.result.query}`,
      `  retrieved_at: ${(/* @__PURE__ */ new Date()).toISOString()}`
    ].join("\n");
    const lineCount = editor.lineCount();
    if (lineCount > 0 && editor.getLine(0).trim() === "---") {
      for (let i = 1; i < lineCount; i++) {
        if (editor.getLine(i).trim() === "---") {
          editor.replaceRange(`${context}
`, { line: i, ch: 0 });
          new import_obsidian2.Notice("Frontmatter updated.");
          return;
        }
      }
    }
    editor.replaceRange(`---
${context}
---
`, { line: 0, ch: 0 });
    new import_obsidian2.Notice("Frontmatter added.");
  }
};
var RouterSettingTab = class extends import_obsidian2.PluginSettingTab {
  constructor(plugin) {
    super(plugin.app, plugin);
    this.plugin = plugin;
  }
  display() {
    const { containerEl } = this;
    containerEl.empty();
    new import_obsidian2.Setting(containerEl).setName("Sidecar endpoint").setDesc("Defaults to a loopback-only Python sidecar.").addText(
      (text) => text.setPlaceholder("http://127.0.0.1:8765").setValue(this.plugin.settings.endpoint).onChange(async (value) => {
        this.plugin.settings.endpoint = value.trim();
        await this.plugin.saveSettings();
      })
    );
    new import_obsidian2.Setting(containerEl).setName("Allow remote endpoint").setDesc("Sends query text outside this device. Leave disabled for local use.").addToggle(
      (toggle) => toggle.setValue(this.plugin.settings.allowRemoteEndpoint).onChange(async (value) => {
        this.plugin.settings.allowRemoteEndpoint = value;
        await this.plugin.saveSettings();
        this.display();
      })
    );
    if (this.plugin.settings.allowRemoteEndpoint) {
      containerEl.createDiv({
        cls: "sanyuan-context-warning",
        text: "Remote mode is enabled. Queries and note paths are sent to the configured host."
      });
    }
    new import_obsidian2.Setting(containerEl).setName("Sidecar token").setDesc("Optional bearer token. This is not an embedding-provider API key.").addText((text) => {
      text.inputEl.type = "password";
      text.setValue(this.plugin.settings.authToken).onChange(async (value) => {
        this.plugin.settings.authToken = value;
        await this.plugin.saveSettings();
      });
    });
    new import_obsidian2.Setting(containerEl).setName("Result count").setDesc("Number of candidates retained after reranking (1\u201332).").addText(
      (text) => text.setValue(String(this.plugin.settings.topK)).onChange(async (value) => {
        const parsed = Number.parseInt(value, 10);
        if (Number.isFinite(parsed)) {
          this.plugin.settings.topK = Math.max(1, Math.min(32, parsed));
          await this.plugin.saveSettings();
        }
      })
    );
    new import_obsidian2.Setting(containerEl).setName("Retrieval mode").addDropdown(
      (dropdown) => dropdown.addOption("full", "Full").addOption("fast", "Fast").addOption("minimal", "Minimal").setValue(this.plugin.settings.mode).onChange(async (value) => {
        if (value === "full" || value === "fast" || value === "minimal") {
          this.plugin.settings.mode = value;
          await this.plugin.saveSettings();
        }
      })
    );
    new import_obsidian2.Setting(containerEl).setName("Smart command trigger").setDesc("Auto uses a conservative intent rule inside the Python pipeline.").addDropdown(
      (dropdown) => dropdown.addOption("auto", "Auto").addOption("always", "Always").addOption("never", "Never").setValue(this.plugin.settings.smartTriggerPolicy).onChange(async (value) => {
        if (value === "auto" || value === "always" || value === "never") {
          this.plugin.settings.smartTriggerPolicy = value;
          await this.plugin.saveSettings();
        }
      })
    );
  }
};
var SanyuanContextRouter = class extends import_obsidian2.Plugin {
  constructor() {
    super(...arguments);
    this.settings = DEFAULT_SETTINGS;
  }
  async onload() {
    await this.loadSettings();
    this.addSettingTab(new RouterSettingTab(this));
    this.addRibbonIcon("search", "Retrieve Sanyuan context", () => {
      var _a;
      const editor = (_a = this.app.workspace.getActiveViewOfType(import_obsidian2.MarkdownView)) == null ? void 0 : _a.editor;
      this.openQuery(editor, "always");
    });
    this.addCommand({
      id: "retrieve-context",
      name: "Retrieve context",
      editorCallback: (editor) => {
        void this.runFromEditor(editor, "always");
      }
    });
    this.addCommand({
      id: "smart-retrieve-context",
      name: "Smart retrieve context",
      editorCallback: (editor) => {
        void this.runFromEditor(editor, this.settings.smartTriggerPolicy);
      }
    });
    this.addCommand({
      id: "check-sidecar",
      name: "Check sidecar",
      callback: () => {
        void this.checkHealth();
      }
    });
    this.addCommand({
      id: "browse-sanyuan-nodes",
      name: "Browse Sanyuan nodes",
      callback: () => {
        void this.browseNodes();
      }
    });
  }
  async loadSettings() {
    const stored = await this.loadData();
    this.settings = Object.assign({}, DEFAULT_SETTINGS, stored != null ? stored : {});
  }
  async saveSettings() {
    await this.saveData(this.settings);
  }
  openQuery(editor, policy) {
    new QueryModal(this, async (query) => this.retrieve(query, policy, editor)).open();
  }
  async runFromEditor(editor, policy) {
    const selection = editor.getSelection().trim();
    if (!selection) {
      this.openQuery(editor, policy);
      return;
    }
    await this.retrieve(selection, policy, editor);
  }
  queryAxes() {
    var _a;
    const activeFile = this.app.workspace.getActiveFile();
    if (!activeFile) {
      return void 0;
    }
    const frontmatter = (_a = this.app.metadataCache.getFileCache(activeFile)) == null ? void 0 : _a.frontmatter;
    return parseAxes(frontmatter == null ? void 0 : frontmatter.sanyuan_axes);
  }
  async retrieve(query, policy, editor) {
    const activeFile = this.app.workspace.getActiveFile();
    const client = new SanyuanClient(this.settings);
    try {
      const result = await client.retrieve({
        query,
        top_k: this.settings.topK,
        mode: this.settings.mode,
        trigger_policy: policy,
        query_axes: this.queryAxes(),
        current_path: activeFile == null ? void 0 : activeFile.path
      });
      new ResultModal(this, result, editor).open();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown retrieval error";
      new import_obsidian2.Notice(message, 8e3);
    }
  }
  async checkHealth() {
    try {
      const health = await new SanyuanClient(this.settings).health();
      new import_obsidian2.Notice(
        `Sidecar: ${health.status}; embeddings: ${health.embedding_enabled ? "on" : "off"}; routing: ${health.routing_loaded ? "on" : "off"}`,
        7e3
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Sidecar health check failed";
      new import_obsidian2.Notice(message, 8e3);
    }
  }
  async browseNodes() {
    var _a;
    const client = new SanyuanClient(this.settings);
    try {
      const result = await client.retrieve({ query: "latest", top_k: this.settings.topK, mode: this.settings.mode, trigger_policy: "always" });
      const candidates = (_a = result.diagnostics) == null ? void 0 : _a.candidates;
      const count = Array.isArray(candidates) ? candidates.length : 0;
      new import_obsidian2.Notice("Browse: retrieved " + count + " candidates", 5e3);
      new ResultModal(this, result).open();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Browse failed";
      new import_obsidian2.Notice(message, 8e3);
    }
  }
};
