import {
  ButtonComponent,
  Editor,
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TextAreaComponent
} from "obsidian";

import { SanyuanClient } from "./client";
import {
  DEFAULT_SETTINGS,
  type RetrieveResponse,
  type RouterSettings,
  type TriggerPolicy
} from "./types";

function parseAxes(value: unknown): string[] | undefined {
  if (Array.isArray(value)) {
    const axes = value.map(String).map((axis) => axis.trim()).filter(Boolean);
    return axes.length ? axes : undefined;
  }
  if (typeof value === "string") {
    const axes = value.split(",").map((axis) => axis.trim()).filter(Boolean);
    return axes.length ? axes : undefined;
  }
  return undefined;
}

class QueryModal extends Modal {
  private query = "";

  constructor(
    plugin: SanyuanContextRouter,
    private readonly submit: (query: string) => Promise<void>
  ) {
    super(plugin.app);
  }

  onOpen(): void {
    this.setTitle("Retrieve context");
    const input = new TextAreaComponent(this.contentEl)
      .setPlaceholder("Enter a retrieval query")
      .onChange((value) => {
        this.query = value;
      });
    input.inputEl.rows = 5;
    input.inputEl.addClass("sanyuan-context-query");
    const actions = this.contentEl.createDiv({ cls: "sanyuan-context-actions" });
    new ButtonComponent(actions)
      .setButtonText("Retrieve")
      .setCta()
      .onClick(() => {
        const query = this.query.trim();
        if (!query) {
          new Notice("Enter a query first.");
          return;
        }
        this.close();
        void this.submit(query);
      });
  }

  onClose(): void {
    this.contentEl.empty();
  }
}

class ResultModal extends Modal {
  constructor(
    plugin: SanyuanContextRouter,
    private readonly result: RetrieveResponse,
    private readonly editor?: Editor
  ) {
    super(plugin.app);
  }

  onOpen(): void {
    this.setTitle(this.result.triggered ? "Retrieved context" : "Retrieval skipped");
    const output = this.contentEl.createEl("pre", {
      cls: "sanyuan-context-result",
      text: this.result.injection
    });
    output.setAttr("tabindex", "0");
    const actions = this.contentEl.createDiv({ cls: "sanyuan-context-actions" });
    new ButtonComponent(actions).setButtonText("Copy").onClick(() => {
      void navigator.clipboard
        .writeText(this.result.injection)
        .then(() => {
          new Notice("Context copied.");
        })
        .catch(() => {
          new Notice("Clipboard access failed. Select the preview text instead.", 7000);
        });
    });
    if (this.editor && this.result.triggered) {
      new ButtonComponent(actions).setButtonText("Insert").setCta().onClick(() => {
        this.editor?.replaceSelection(`\n\n${this.result.injection}\n`);
        this.close();
      });
    }
  }

  onClose(): void {
    this.contentEl.empty();
  }
}

class RouterSettingTab extends PluginSettingTab {
  constructor(private readonly plugin: SanyuanContextRouter) {
    super(plugin.app, plugin);
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    new Setting(containerEl)
      .setName("Sidecar endpoint")
      .setDesc("Defaults to a loopback-only Python sidecar.")
      .addText((text) =>
        text
          .setPlaceholder("http://127.0.0.1:8765")
          .setValue(this.plugin.settings.endpoint)
          .onChange(async (value) => {
            this.plugin.settings.endpoint = value.trim();
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Allow remote endpoint")
      .setDesc("Sends query text outside this device. Leave disabled for local use.")
      .addToggle((toggle) =>
        toggle
          .setValue(this.plugin.settings.allowRemoteEndpoint)
          .onChange(async (value) => {
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

    new Setting(containerEl)
      .setName("Sidecar token")
      .setDesc("Optional bearer token. This is not an embedding-provider API key.")
      .addText((text) => {
        text.inputEl.type = "password";
        text.setValue(this.plugin.settings.authToken).onChange(async (value) => {
          this.plugin.settings.authToken = value;
          await this.plugin.saveSettings();
        });
      });

    new Setting(containerEl)
      .setName("Result count")
      .setDesc("Number of candidates retained after reranking (1–32).")
      .addText((text) =>
        text.setValue(String(this.plugin.settings.topK)).onChange(async (value) => {
          const parsed = Number.parseInt(value, 10);
          if (Number.isFinite(parsed)) {
            this.plugin.settings.topK = Math.max(1, Math.min(32, parsed));
            await this.plugin.saveSettings();
          }
        })
      );

    new Setting(containerEl).setName("Retrieval mode").addDropdown((dropdown) =>
      dropdown
        .addOption("full", "Full")
        .addOption("fast", "Fast")
        .addOption("minimal", "Minimal")
        .setValue(this.plugin.settings.mode)
        .onChange(async (value) => {
          if (value === "full" || value === "fast" || value === "minimal") {
            this.plugin.settings.mode = value;
            await this.plugin.saveSettings();
          }
        })
    );

    new Setting(containerEl)
      .setName("Smart command trigger")
      .setDesc("Auto uses a conservative intent rule inside the Python pipeline.")
      .addDropdown((dropdown) =>
        dropdown
          .addOption("auto", "Auto")
          .addOption("always", "Always")
          .addOption("never", "Never")
          .setValue(this.plugin.settings.smartTriggerPolicy)
          .onChange(async (value) => {
            if (value === "auto" || value === "always" || value === "never") {
              this.plugin.settings.smartTriggerPolicy = value;
              await this.plugin.saveSettings();
            }
          })
      );
  }
}

export default class SanyuanContextRouter extends Plugin {
  settings: RouterSettings = DEFAULT_SETTINGS;

  async onload(): Promise<void> {
    await this.loadSettings();
    this.addSettingTab(new RouterSettingTab(this));

    this.addRibbonIcon("search", "Retrieve Sanyuan context", () => {
      const editor = this.app.workspace.getActiveViewOfType(MarkdownView)?.editor;
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
  }

  async loadSettings(): Promise<void> {
    const stored = (await this.loadData()) as Partial<RouterSettings> | null;
    this.settings = Object.assign({}, DEFAULT_SETTINGS, stored ?? {});
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }

  private openQuery(editor: Editor | undefined, policy: TriggerPolicy): void {
    new QueryModal(this, async (query) => this.retrieve(query, policy, editor)).open();
  }

  private async runFromEditor(editor: Editor, policy: TriggerPolicy): Promise<void> {
    const selection = editor.getSelection().trim();
    if (!selection) {
      this.openQuery(editor, policy);
      return;
    }
    await this.retrieve(selection, policy, editor);
  }

  private queryAxes(): string[] | undefined {
    const activeFile = this.app.workspace.getActiveFile();
    if (!activeFile) {
      return undefined;
    }
    const frontmatter = this.app.metadataCache.getFileCache(activeFile)?.frontmatter;
    return parseAxes(frontmatter?.sanyuan_axes);
  }

  private async retrieve(
    query: string,
    policy: TriggerPolicy,
    editor?: Editor
  ): Promise<void> {
    const activeFile = this.app.workspace.getActiveFile();
    const client = new SanyuanClient(this.settings);
    try {
      const result = await client.retrieve({
        query,
        top_k: this.settings.topK,
        mode: this.settings.mode,
        trigger_policy: policy,
        query_axes: this.queryAxes(),
        current_path: activeFile?.path
      });
      new ResultModal(this, result, editor).open();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Unknown retrieval error";
      new Notice(message, 8000);
    }
  }

  private async checkHealth(): Promise<void> {
    try {
      const health = await new SanyuanClient(this.settings).health();
      new Notice(
        `Sidecar: ${health.status}; embeddings: ${health.embedding_enabled ? "on" : "off"}; routing: ${health.routing_loaded ? "on" : "off"}`,
        7000
      );
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Sidecar health check failed";
      new Notice(message, 8000);
    }
  }
}
