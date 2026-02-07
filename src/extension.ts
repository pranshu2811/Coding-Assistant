import * as vscode from 'vscode';
type RefactorResponse = {
	refactored?: string;
	code?: string;
};


export function activate(context: vscode.ExtensionContext) {
	console.log('local-ai-coding-assistant active');

	const disposable = vscode.commands.registerCommand(
		'local-ai-coding-assistant.helloWorld',
		async () => {
			const editor = vscode.window.activeTextEditor;
			if (!editor) {
				vscode.window.showInformationMessage('No active editor – open a file first.');
				return;
			}

			const document = editor.document;
			const fullText = document.getText();

			try {
				// 1) Call your local API
				const response = await fetch('http://localhost:8000/refactor', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ code: fullText })
				});

				if (!response.ok) {
					vscode.window.showErrorMessage(`Refactor failed: ${response.statusText}`);
					return;
				}

				const data = (await response.json()) as RefactorResponse;
				const newCode = data.refactored ?? data.code ?? '';

				// 2) Replace entire document with the refactored code
				const fullRange = new vscode.Range(
					document.positionAt(0),
					document.positionAt(fullText.length)
				);

				await editor.edit(editBuilder => {
					editBuilder.replace(fullRange, newCode);
				});

				vscode.window.showInformationMessage('Refactor complete.');
			} catch (err: any) {
				vscode.window.showErrorMessage(`Error calling local AI: ${err.message ?? err}`);
			}
		}
	);

	context.subscriptions.push(disposable);
}

export function deactivate() { }
