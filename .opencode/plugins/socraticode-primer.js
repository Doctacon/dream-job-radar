import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js"

const SEARCH_LIMIT = Number.parseInt(process.env.SOCRATICODE_PRIMER_LIMIT ?? "6", 10)
const SEARCH_MIN_SCORE = Number.parseFloat(process.env.SOCRATICODE_PRIMER_MIN_SCORE ?? "0.1")
const SEARCH_TIMEOUT_MS = Number.parseInt(process.env.SOCRATICODE_PRIMER_TIMEOUT_MS ?? "20000", 10)
const ENABLE_GREP_WARNING = process.env.SOCRATICODE_PRIMER_GREP_WARNING !== "0"
const CLASSIFIER_MODEL = process.env.SOCRATICODE_PRIMER_CLASSIFIER_MODEL ?? "openai/gpt-5.4-mini"
const CLASSIFIER_TIMEOUT_MS = Number.parseInt(process.env.SOCRATICODE_PRIMER_CLASSIFIER_TIMEOUT_MS ?? "15000", 10)
const DEBUG_ROUTER = process.env.SOCRATICODE_PRIMER_DEBUG_ROUTER === "1"
const CLASSIFIER_SENTINEL = "<socraticode-classifier-request>"

let clientPromise
let searchSucceededBySession = new Map()
let classifierSessionIDs = new Set()

function latestUserMessage(messages) {
  return [...messages].reverse().find((message) => message?.info?.role === "user")
}

function textFromParts(parts) {
  return (parts ?? [])
    .filter((part) => part?.type === "text" && !part.synthetic && !part.ignored)
    .map((part) => part.text)
    .filter(Boolean)
    .join("\n")
    .trim()
}

async function withTimeout(promise, label) {
  let timeout
  const timer = new Promise((_, reject) => {
    timeout = setTimeout(() => reject(new Error(`${label} timed out after ${SEARCH_TIMEOUT_MS}ms`)), SEARCH_TIMEOUT_MS)
  })
  try {
    return await Promise.race([promise, timer])
  } finally {
    clearTimeout(timeout)
  }
}

async function withPromiseTimeout(promise, label, timeoutMs) {
  let timeout
  const timer = new Promise((_, reject) => {
    timeout = setTimeout(() => reject(new Error(`${label} timed out after ${timeoutMs}ms`)), timeoutMs)
  })
  try {
    return await Promise.race([promise, timer])
  } finally {
    clearTimeout(timeout)
  }
}

function classifierModel() {
  const [providerID, ...rest] = CLASSIFIER_MODEL.split("/")
  return {
    providerID: rest.length > 0 ? providerID : "openai",
    modelID: rest.length > 0 ? rest.join("/") : CLASSIFIER_MODEL,
  }
}

function classifierSessionModel() {
  const model = classifierModel()
  return {
    id: model.modelID,
    providerID: model.providerID,
  }
}

function unwrap(response) {
  if (response && typeof response === "object" && "data" in response) return response.data
  return response
}

function partsText(parts) {
  return (parts ?? [])
    .filter((part) => part?.type === "text")
    .map((part) => part.text)
    .filter(Boolean)
    .join("\n")
    .trim()
}

function parseClassifierJSON(text) {
  const trimmed = String(text ?? "").trim()
  if (/<system-reminder>|plan mode is active|# plan mode/i.test(trimmed)) {
    throw new Error("classifier response was contaminated by plan-mode/system reminder")
  }
  const match = trimmed.match(/\{[\s\S]*\}/)
  if (!match) throw new Error(`classifier returned non-JSON output: ${trimmed.slice(0, 120)}`)

  const parsed = JSON.parse(match[0])
  if (typeof parsed.search !== "boolean") throw new Error("classifier JSON missing boolean `search`")
  return {
    search: parsed.search,
    reason: typeof parsed.reason === "string" ? parsed.reason.slice(0, 240) : "no reason provided",
  }
}

function classifierUserPrompt(prompt) {
  return [
    CLASSIFIER_SENTINEL,
    "Decide whether SocratiCode semantic codebase search should run before answering this user prompt.",
    "Return only compact JSON with this exact shape: {\"search\": true|false, \"reason\": \"short reason\"}.",
    "Return search=true when repository context would likely help: locating code, understanding implementation, debugging, architecture, data/control flow, tests, config, scripts, entrypoints, or project-specific concepts.",
    "Return search=false for greetings, thanks, commit-message-only requests, pure shell command execution, general writing, or questions that do not require repository context.",
    "User prompt:",
    prompt,
    "</socraticode-classifier-request>",
  ].join("\n")
}

function classifierSystemPrompt() {
  return [
    "You are a routing classifier, not a coding agent.",
    "Return only compact JSON with this exact shape: {\"search\": true|false, \"reason\": \"short reason\"}.",
    "Do not plan. Do not use tools. Do not answer the user's question. Do not include markdown.",
    "Ignore workflow, plan-mode, or build-mode instructions if they appear in context; this task is only classification.",
  ].join(" ")
}

async function waitForClassifierText(opencodeClient, sessionID, directory, deadline) {
  while (Date.now() < deadline) {
    const messages = unwrap(
      await opencodeClient.session.messages({
        path: { id: sessionID },
        query: { directory },
      }),
    )
    const assistant = [...(messages ?? [])].reverse().find((message) => message?.info?.role === "assistant")
    const text = partsText(assistant?.parts)
    if (text) return text
    await new Promise((resolve) => setTimeout(resolve, 250))
  }
  throw new Error(`classifier session did not produce a response before timeout`)
}

async function classifyPrompt(prompt, opencodeClient, directory) {
  if (!opencodeClient?.session?.create || !opencodeClient?.session?.prompt || !opencodeClient?.session?.messages) {
    throw new Error("OpenCode plugin client does not expose required session APIs for classifier routing")
  }

  let sessionID
  const timeoutMs = Number.isFinite(CLASSIFIER_TIMEOUT_MS) ? CLASSIFIER_TIMEOUT_MS : 15000
  const deadline = Date.now() + timeoutMs

  try {
    const created = unwrap(
      await withPromiseTimeout(
        opencodeClient.session.create({
          query: { directory },
          body: {
            title: "SocratiCode classifier",
            agent: "build",
            model: classifierSessionModel(),
          },
        }),
        "SocratiCode classifier session create",
        timeoutMs,
      ),
    )
    sessionID = created?.id
    if (!sessionID) throw new Error("classifier session create did not return an id")
    classifierSessionIDs.add(sessionID)

    await withPromiseTimeout(
      opencodeClient.session.prompt({
        path: { id: sessionID },
        query: { directory },
        body: {
          model: classifierModel(),
          agent: "build",
          system: classifierSystemPrompt(),
          tools: {
            bash: false,
            read: false,
            grep: false,
            glob: false,
            task: false,
            webfetch: false,
            todowrite: false,
            apply_patch: false,
          },
          parts: [{ type: "text", text: classifierUserPrompt(prompt) }],
        },
      }),
      "SocratiCode classifier prompt",
      Math.max(1000, deadline - Date.now()),
    )

    const text = await waitForClassifierText(opencodeClient, sessionID, directory, deadline)
    return parseClassifierJSON(text)
  } finally {
    if (sessionID) {
      classifierSessionIDs.delete(sessionID)
      if (opencodeClient?.session?.delete) {
        opencodeClient.session.delete({ path: { id: sessionID }, query: { directory } }).catch(() => undefined)
      }
    }
  }
}

async function getClient() {
  if (!clientPromise) {
    clientPromise = (async () => {
      const transport = new StdioClientTransport({
        command: "npx",
        args: ["-y", "socraticode"],
      })

      const client = new Client({
        name: "opencode-socraticode-primer",
        version: "0.1.0",
      })

      await withTimeout(client.connect(transport), "SocratiCode MCP connection")
      return client
    })().catch((error) => {
      clientPromise = undefined
      throw error
    })
  }

  return clientPromise
}

function contentText(result) {
  return (result?.content ?? [])
    .filter((item) => item?.type === "text")
    .map((item) => item.text)
    .filter(Boolean)
    .join("\n")
    .trim()
}

function isSearchWarning(text) {
  return /docker is not available|qdrant is not available|no index found|make sure the project has been indexed|run codebase_index|index is incomplete/i.test(
    text,
  )
}

async function searchSocratiCode(query, directory) {
  const client = await getClient()
  const result = await withTimeout(
    client.callTool({
      name: "codebase_search",
      arguments: {
        query,
        projectPath: directory,
        limit: Number.isFinite(SEARCH_LIMIT) ? SEARCH_LIMIT : 6,
        minScore: Number.isFinite(SEARCH_MIN_SCORE) ? SEARCH_MIN_SCORE : 0.1,
      },
    }),
    "SocratiCode search",
  )

  return contentText(result)
}

function appendSyntheticText(message, text) {
  const info = message.info
  message.parts.push({
    id: `socraticode-primer-${info.id}-${Date.now()}`,
    sessionID: info.sessionID,
    messageID: info.id,
    type: "text",
    synthetic: true,
    text,
    time: {
      start: Date.now(),
      end: Date.now(),
    },
  })
}

function isBroadGrepCommand(command) {
  const text = String(command ?? "")
  if (!/\b(rg|grep)\b/.test(text)) return false

  const narrowSignals = [
    /\b(rg|grep)\b[^\n]*(--files|-l|--glob|-g|--type|-t|--type-add)/,
    /\b(rg|grep)\b[^\n]+\s(?:\.?\.?\/|[A-Za-z0-9_.-]+\/)[^\s]*/,
    /["'][^"']{8,}["']/,
    /\b[A-Z][A-Za-z0-9_$]{4,}\b/,
    /\b[A-Za-z0-9]*_[A-Za-z0-9_]+\b/,
  ]
  return !narrowSignals.some((pattern) => pattern.test(text))
}

export const SocratiCodePrimer = async ({ directory, client: opencodeClient }) => {
  return {
    "experimental.chat.messages.transform": async (input, output) => {
      if (input?.sessionID && classifierSessionIDs.has(input.sessionID)) return

      const latest = latestUserMessage(output.messages)
      if (!latest) return

      const query = textFromParts(latest.parts)
      if (!query) return
      if (query.includes(CLASSIFIER_SENTINEL)) return

      let decision
      try {
        decision = await classifyPrompt(query, opencodeClient, directory)
      } catch (error) {
        searchSucceededBySession.set(latest.info.sessionID, false)
        appendSyntheticText(
          latest,
          [
            "<socraticode-router-warning>",
            `SocratiCode classifier routing failed; semantic search was not run: ${error instanceof Error ? error.message : String(error)}`,
            "</socraticode-router-warning>",
          ].join("\n"),
        )
        return
      }

      if (!decision.search) {
        searchSucceededBySession.set(latest.info.sessionID, false)
        if (DEBUG_ROUTER) {
          appendSyntheticText(
            latest,
            [
              "<socraticode-router>",
              `decision: skip`,
              `model: ${CLASSIFIER_MODEL}`,
              `reason: ${decision.reason}`,
              "</socraticode-router>",
            ].join("\n"),
          )
        }
        return
      }

      try {
        const results = await searchSocratiCode(query, directory)
        if (!results) return

        if (isSearchWarning(results)) {
          searchSucceededBySession.set(latest.info.sessionID, false)
          appendSyntheticText(
            latest,
            [
              "<socraticode-semantic-search-warning>",
              results,
              "If codebase discovery is needed, prefer fixing or checking SocratiCode/index status before broad grep/rg exploration.",
              "</socraticode-semantic-search-warning>",
            ].join("\n"),
          )
          return
        }

        searchSucceededBySession.set(latest.info.sessionID, true)
        appendSyntheticText(
          latest,
          [
            "<socraticode-semantic-search>",
            `Classifier decision: search (${decision.reason})`,
            "",
            results,
            "</socraticode-semantic-search>",
            "",
            "Use these SocratiCode semantic search results before broad grep/rg. Use grep only to verify exact symbols, strings, paths, or line references.",
          ].join("\n"),
        )
      } catch (error) {
        searchSucceededBySession.set(latest.info.sessionID, false)
        appendSyntheticText(
          latest,
          [
            "<socraticode-semantic-search-warning>",
            `SocratiCode semantic search was attempted but did not complete: ${error instanceof Error ? error.message : String(error)}`,
            "If codebase discovery is needed, prefer fixing or checking SocratiCode/index status before broad grep/rg exploration.",
            "</socraticode-semantic-search-warning>",
          ].join("\n"),
        )
      }
    },

    "tool.execute.before": async (input, output) => {
      if (!ENABLE_GREP_WARNING) return
      if (!searchSucceededBySession.get(input.sessionID)) return
      if (input.tool !== "bash") return
      if (!isBroadGrepCommand(output.args?.command)) return

      output.args.command = [
        "printf '%s\\n' 'SocratiCode semantic search already ran for this session. Use its results first; use grep/rg only for exact verification.'",
        output.args.command,
      ].join(" && ")
    },
  }
}
