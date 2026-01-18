export interface HookInput {
	tool_name: string;
	tool_input: {
		command?: string;
	};
	session_id?: string;
	cwd?: string;
}

export interface QualityCheckResult {
	success: boolean;
	checkType: "pre-commit" | "pre-push" | "none";
	output: string;
	failedChecks: string[];
}

export interface HookOutput {
	hookSpecificOutput: {
		hookEventName: string;
		permissionDecision: "allow" | "block" | "ask";
		permissionDecisionReason: string;
	};
}

export interface QualityConfig {
	preCommit: {
		enabled: boolean;
		checks: ("eslint" | "prettier" | "typecheck")[];
	};
	prePush: {
		enabled: boolean;
		checks: ("test" | "build")[];
	};
}
