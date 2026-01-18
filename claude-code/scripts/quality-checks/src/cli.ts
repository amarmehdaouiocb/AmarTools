#!/usr/bin/env bun

import type { HookInput, HookOutput } from "./lib/types";
import { QualityRunner } from "./lib/quality-runner";

async function main() {
	try {
		const stdin = process.stdin;
		const chunks: Buffer[] = [];

		for await (const chunk of stdin) {
			chunks.push(chunk);
		}

		const input = Buffer.concat(chunks).toString();

		if (!input.trim()) {
			console.error("[QUALITY] No input received from stdin");
			process.exit(0); // Allow command to proceed
		}

		let hookData: HookInput;
		try {
			hookData = JSON.parse(input);
		} catch (error) {
			console.error("[QUALITY] Invalid JSON input:", (error as Error).message);
			process.exit(0); // Allow command to proceed
		}

		const toolName = hookData.tool_name || "Unknown";
		const toolInput = hookData.tool_input || {};
		const cwd = hookData.cwd || process.cwd();

		// Only process Bash commands
		if (toolName !== "Bash") {
			process.exit(0);
		}

		const command = toolInput.command;
		if (!command) {
			process.exit(0);
		}

		const runner = new QualityRunner(cwd);
		const commandType = runner.detectCommandType(command);

		// Skip if not a git commit/push command
		if (commandType === "none") {
			process.exit(0);
		}

		console.error(`[QUALITY] Detected ${commandType} command, running checks...`);

		const result = await runner.run(command);

		if (result.success) {
			console.error(`[QUALITY] All ${commandType} checks passed!`);
			process.exit(0); // Allow command to proceed
		}

		// Checks failed - block the command
		const failedList = result.failedChecks.join(", ");
		const blockMessage = `Quality checks failed for ${commandType}!

Failed checks: ${failedList}

${result.output}

Fix the issues above before committing/pushing.`;

		const hookOutput: HookOutput = {
			hookSpecificOutput: {
				hookEventName: "PreToolUse",
				permissionDecision: "block",
				permissionDecisionReason: blockMessage,
			},
		};

		console.log(JSON.stringify(hookOutput));
		process.exit(0);
	} catch (error) {
		console.error("[QUALITY] Hook error:", error);
		process.exit(0); // Allow command to proceed on error
	}
}

main().catch((error) => {
	console.error("[QUALITY] Fatal error:", error);
	process.exit(0); // Allow command to proceed on fatal error
});
