import type { QualityCheckResult, QualityConfig } from "./types";

const DEFAULT_CONFIG: QualityConfig = {
	preCommit: {
		enabled: true,
		checks: ["typecheck", "eslint", "prettier"],
	},
	prePush: {
		enabled: true,
		checks: ["test", "build"],
	},
};

export class QualityRunner {
	private config: QualityConfig;
	private cwd: string;

	constructor(cwd: string, config?: Partial<QualityConfig>) {
		this.cwd = cwd;
		this.config = { ...DEFAULT_CONFIG, ...config };
	}

	detectCommandType(command: string): "pre-commit" | "pre-push" | "none" {
		const normalizedCmd = command.trim().toLowerCase();

		// Detect git commit (but not amend without changes)
		if (/git\s+commit\b/.test(normalizedCmd)) {
			return "pre-commit";
		}

		// Detect git push
		if (/git\s+push\b/.test(normalizedCmd)) {
			return "pre-push";
		}

		return "none";
	}

	async runCheck(
		checkName: string,
	): Promise<{ success: boolean; output: string }> {
		const commands: Record<string, string[]> = {
			eslint: ["npm", "run", "lint"],
			prettier: ["npm", "run", "format:check"],
			typecheck: ["npm", "run", "typecheck"],
			test: ["npm", "run", "test:run"],
			build: ["npm", "run", "build"],
		};

		const cmd = commands[checkName];
		if (!cmd) {
			return { success: false, output: `Unknown check: ${checkName}` };
		}

		try {
			const proc = Bun.spawn(cmd, {
				cwd: this.cwd,
				stdout: "pipe",
				stderr: "pipe",
				env: { ...process.env, FORCE_COLOR: "0" },
			});

			const exitCode = await proc.exited;
			const stdout = await new Response(proc.stdout).text();
			const stderr = await new Response(proc.stderr).text();

			const output = (stdout + stderr).trim();

			return {
				success: exitCode === 0,
				output: output.substring(0, 2000), // Limit output size
			};
		} catch (error) {
			return {
				success: false,
				output: `Failed to run ${checkName}: ${(error as Error).message}`,
			};
		}
	}

	async runPreCommitChecks(): Promise<QualityCheckResult> {
		const result: QualityCheckResult = {
			success: true,
			checkType: "pre-commit",
			output: "",
			failedChecks: [],
		};

		if (!this.config.preCommit.enabled) {
			result.output = "Pre-commit checks disabled";
			return result;
		}

		const outputs: string[] = [];

		for (const check of this.config.preCommit.checks) {
			console.error(`[QUALITY] Running ${check}...`);
			const checkResult = await this.runCheck(check);

			if (!checkResult.success) {
				result.success = false;
				result.failedChecks.push(check);
				outputs.push(`\n--- ${check.toUpperCase()} FAILED ---\n${checkResult.output}`);
			} else {
				outputs.push(`[OK] ${check}`);
			}
		}

		result.output = outputs.join("\n");
		return result;
	}

	async runPrePushChecks(): Promise<QualityCheckResult> {
		const result: QualityCheckResult = {
			success: true,
			checkType: "pre-push",
			output: "",
			failedChecks: [],
		};

		if (!this.config.prePush.enabled) {
			result.output = "Pre-push checks disabled";
			return result;
		}

		const outputs: string[] = [];

		for (const check of this.config.prePush.checks) {
			console.error(`[QUALITY] Running ${check}...`);
			const checkResult = await this.runCheck(check);

			if (!checkResult.success) {
				result.success = false;
				result.failedChecks.push(check);
				outputs.push(`\n--- ${check.toUpperCase()} FAILED ---\n${checkResult.output}`);
			} else {
				outputs.push(`[OK] ${check}`);
			}
		}

		result.output = outputs.join("\n");
		return result;
	}

	async run(command: string): Promise<QualityCheckResult> {
		const commandType = this.detectCommandType(command);

		if (commandType === "none") {
			return {
				success: true,
				checkType: "none",
				output: "",
				failedChecks: [],
			};
		}

		if (commandType === "pre-commit") {
			return this.runPreCommitChecks();
		}

		return this.runPrePushChecks();
	}
}
